import cv2
import numpy as np
import base64
import openai
import tempfile
import os
from google.cloud import vision_v1
import logging
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
import gc
import io
from functools import wraps

def timeout_handler(timeout_seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, *args, **kwargs)
                    return future.result(timeout=timeout_seconds)
            except (TimeoutError, Exception) as e:
                elapsed_time = time.time() - start_time
                logging.warning(f"Function {func.__name__} timed out after {elapsed_time:.2f} seconds: {str(e)}")
                return 'clear'  # Return clear on timeout as requested
        return wrapper
    return decorator

class LivenessDetector:
    def __init__(self, client, openai_api_key):
        self.google_client = client
        openai.api_key = openai_api_key

    def extract_frames(self, video_path, frame_count=2, frame_positions='middle'):
        """Extract frames from video based on count and positions.
        frame_positions can be: 'middle' (frames from middle section) or 'distributed' (evenly distributed frames)
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if frame_positions == 'middle':
                # Get frames from middle section
                mid_point = total_frames // 2
                start_idx = mid_point - (frame_count // 2)
                frame_indices = range(start_idx, start_idx + frame_count)
            else:
                # Get evenly distributed frames
                step = total_frames // (frame_count + 1)
                frame_indices = [i * step for i in range(1, frame_count + 1)]
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # Resize frame to reduce memory usage and processing time
                    frame = cv2.resize(frame, (480, 360))  # Reduced resolution
                    frames.append(frame)
                    
        finally:
            cap.release()
            gc.collect()
        return frames

    def image_to_base64(self, image):
        """Convert image to base64 string with aggressive compression."""
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Aggressive JPEG compression
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]  # Reduced quality
            _, buffer = cv2.imencode('.jpg', image, encode_param)
            return base64.b64encode(buffer).decode('utf-8')
        finally:
            del buffer
            gc.collect()

    def analyze_frame_openai(self, frame):
        """Analyze frame using OpenAI's GPT-4 Vision."""
        try:
            base64_image = self.image_to_base64(frame)
            
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Check this frame for liveness. Detect if person is physically present or spoofing. Look for moiré patterns, pixelation, screen bezels, photo of a photo, video from a phone, or video from a screen and other signs of spoofing. Return only dictionary without any text like json, python,..: {is_live:bool,confidence:0-100}. Only return is_live as false if you are sure that the person is spoofing and confidenece is more than 85. If a person seems to be recording a video displayed on a screen(any display device), return is_live as false. Make sure to not flag is_live as false if the person is not found to do spoofing."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            logging.error(f"Error analyzing frame with OpenAI: {str(e)}")
            return None
        finally:
            del base64_image
            gc.collect()

    def analyze_final_results(self, frame_results):
        """Quick analysis of frame results."""
        try:
            analysis_prompt = f"""Analyze these video frame results for liveness detection:
            {frame_results}
            Return only dictionary, no other text like json, python, or anything else, only dictionary in your response with is_person_live value to be a boolean(true/false):
            {{"is_person_live": true/false, "confidence": 0-100}}"""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=50
            )
            
            return response.choices[0].message['content']
        except Exception as e:
            logging.error(f"Error in final OpenAI analysis: {str(e)}")
            return None
        finally:
            gc.collect()

    def calculate_landmarks_movement(self, current_landmarks, previous_landmarks):
        try:
            return sum(
                abs(cur_point.position.x - prev_point.position.x) +
                abs(cur_point.position.y - prev_point.position.y)
                for cur_point, prev_point in zip(current_landmarks, previous_landmarks)
            )
        finally:
            gc.collect()

    def calculate_face_movement(self, current_face, previous_face):
        try:
            return abs(current_face[0].x - previous_face[0].x) + abs(current_face[0].y - previous_face[0].y)
        finally:
            gc.collect()

    def calculate_liveness_result(self, eyebrow_movement, nose_movement, lip_movement, face_movement):
        eyebrow_movement_threshold = 15.0
        nose_movement_threshold = 15.0
        lip_movement_threshold = 15.0
        face_movement_threshold = 10.0
        
        return any([
            eyebrow_movement > eyebrow_movement_threshold,
            nose_movement > nose_movement_threshold,
            lip_movement > lip_movement_threshold,
            face_movement > face_movement_threshold
        ])

    @timeout_handler(7)  # 7 second timeout for Google check
    def check_google_liveness(self, video_path):
        """Optimized Google Vision API check with 4 distributed frames."""
        try:
            frames = self.extract_frames(video_path, frame_count=4, frame_positions='distributed')
            if not frames:
                return 'clear'  # Changed to return clear

            previous_landmarks = None
            previous_face = None
            liveness_result_list = []

            # Process frames in parallel
            def process_frame(frame):
                _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
                image = vision_v1.Image(content=buffer.tobytes())
                response = self.google_client.face_detection(image=image)
                return response.face_annotations

            with ThreadPoolExecutor(max_workers=2) as executor:
                face_results = list(executor.map(process_frame, frames))

            for faces in face_results:
                if not faces:
                    continue

                largest_face = max(faces, key=lambda face: 
                    abs((face.bounding_poly.vertices[2].x - face.bounding_poly.vertices[0].x) * 
                        (face.bounding_poly.vertices[2].y - face.bounding_poly.vertices[0].y)))

                current_landmarks = largest_face.landmarks
                current_face = largest_face.bounding_poly.vertices

                if previous_landmarks and previous_face:
                    movements = [
                        self.calculate_landmarks_movement(current_landmarks[:10], previous_landmarks[:10]),  # eyebrows
                        self.calculate_landmarks_movement(current_landmarks[10:20], previous_landmarks[10:20]),  # nose
                        self.calculate_landmarks_movement(current_landmarks[20:28], previous_landmarks[20:28]),  # lips
                        self.calculate_face_movement(current_face, previous_face)  # face
                    ]
                    
                    thresholds = [15.0, 15.0, 15.0, 10.0]  # eyebrow, nose, lip, face thresholds
                    liveness_result = any(m > t for m, t in zip(movements, thresholds))
                    liveness_result_list.append(liveness_result)

                previous_landmarks = current_landmarks
                previous_face = current_face

            return 'clear' if any(liveness_result_list) else 'consider'

        except Exception as e:
            logging.error(f"Error in Google Vision check: {str(e)}")
            return 'clear'  # Changed to return clear
        finally:
            gc.collect()

    @timeout_handler(9)  # 9 second timeout for OpenAI check
    def check_openai_liveness(self, video_path):
        """Optimized OpenAI check with parallel processing of middle frames."""
        try:
            start_time = time.time()
            frames = self.extract_frames(video_path, frame_count=3, frame_positions='middle')
            extract_time = time.time() - start_time
            logging.info(f"Frame extraction took: {extract_time:.2f} seconds")

            if not frames:
                return 'clear'  # Changed to return clear

            # Process frames in parallel
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=3) as executor:
                frame_futures = [executor.submit(self.analyze_frame_openai, frame) for frame in frames]
                frame_results = []
                for future in as_completed(frame_futures):
                    try:
                        result = future.result(timeout=3)  # 3 second timeout per frame
                        if result:
                            frame_results.append(str(result))
                            print(f"\nAI Response: {result}\n")
                    except TimeoutError:
                        logging.warning("Frame analysis timed out")
                        return 'clear'

            if not frame_results:
                return 'clear'  # Changed to return clear

            # Calculate majority vote
            try:
                true_votes = sum('true' in value.lower() for value in frame_results)
                return 'clear' if true_votes > len(frame_results) // 2 else 'consider'
            except Exception as e:
                logging.error(f"Error processing OpenAI responses: {str(e)}")
                return 'clear'  # Changed to return clear

        except Exception as e:
            logging.error(f"Error in OpenAI check: {str(e)}")
            return 'clear'  # Changed to return clear
        finally:
            gc.collect()

    @timeout_handler(15)  # 15 second timeout for entire check_liveness method
    def check_liveness(self, video_bytes):
        """Optimized parallel liveness check with benchmarking."""
        temp_video_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        temp_video_file_path = temp_video_file.name
        
        try:
            # Write video bytes efficiently
            write_start = time.time()
            with open(temp_video_file_path, 'wb') as f:
                f.write(video_bytes)
            del video_bytes
            gc.collect()
            logging.info(f"Video write took: {time.time() - write_start:.2f} seconds")

            # Run checks in parallel with shorter timeouts
            check_start = time.time()
            with ThreadPoolExecutor(max_workers=2) as executor:
                future_google = executor.submit(self.check_google_liveness, temp_video_file_path)
                future_openai = executor.submit(self.check_openai_liveness, temp_video_file_path)

                try:
                    # Wait for both results with shorter timeout to ensure total process stays under 15s
                    google_result = future_google.result(timeout=5)
                    openai_result = future_openai.result(timeout=9)

                    check_time = time.time() - check_start
                    logging.info(f":--------------Parallel checks took: {check_time:.2f} seconds")
                    print(f'\nMotion tracking Result: {google_result}\nAI Analysis Result: {openai_result}\n')

                    return 'clear' if google_result == 'clear' and openai_result == 'clear' else 'consider'
                except TimeoutError:
                    logging.warning("Individual checks timed out, returning clear as fallback")
                    return 'clear'

        except Exception as e:
            logging.error(f"Error in liveness check: {str(e)}")
            return 'clear'  # Changed to return clear on error as per timeout requirement
        finally:
            if os.path.exists(temp_video_file_path):
                os.remove(temp_video_file_path)
            gc.collect() 