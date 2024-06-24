# Ultrasound sensors are directly implemented onto the Arduino code
import pyrealsense2 as rs
import numpy as np
import cv2
import time
import pygame
import os
from concurrent.futures import ThreadPoolExecutor

event_occurred = False
file_name = 'distancias.txt'

def initialize_file():
    with open(file_name, 'w') as file:
        file.write(f'\n')

def write_to_file(message):
    with open(file_name, 'w') as file:
        file.write(f'{message}\n')

def stop_measurements(pipeline_l515=None, pipeline_d435=None):
    write_to_file(f'p\n')
    if pipeline_l515:
        pipeline_l515.stop()
    if pipeline_d435:
        pipeline_d435.stop()
    cv2.destroyAllWindows()
    os._exit(0)

def play_beep():
    pygame.init()
    alarm_sound_path = "C:/Users/Lara/Desktop/TFG/pending-notification.wav"
    pygame.mixer.music.load(alarm_sound_path)
    pygame.mixer.music.play()
    pygame.time.wait(1000)
    pygame.mixer.music.stop()
    pygame.quit()

def configure_camera_l515(config):
    config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)

def configure_camera_d435(config):
    config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)

def check_d435_connected():
    ctx = rs.context()
    devices = ctx.query_devices()
    d435_found = False
    
    for dev in devices:
        if 'D435' in dev.get_info(rs.camera_info.name):
            print("Intel RealSense D435 found:", dev.get_info(rs.camera_info.name))
            d435_found = True
    
    if not d435_found:
        print("No Intel RealSense D435 found.")
        return False
    return True

def check_l515_connected():
    ctx = rs.context()
    devices = ctx.query_devices()
    l515_found = False
    
    for dev in devices:
        if 'L515' in dev.get_info(rs.camera_info.name):
            print("Intel RealSense L515 found:", dev.get_info(rs.camera_info.name))
            l515_found = True
    
    if not l515_found:
        print("No Intel RealSense L515 found.")
        return False
    return True       

def get_central_pixel_coordinates(width, height, cell_x, cell_y, cell_width, cell_height):
    cell_center_x = ((cell_x * cell_width) + (cell_width // 2))
    cell_center_y = ((cell_y * cell_height) + (cell_height // 2))
    return cell_center_x, cell_center_y

def calculate_d_security(dS, dMi, dC, alpha_deg, beta_deg, pixel_yi, pixel_y, pixel_ymax_2):
    alpha = np.radians(alpha_deg)
    beta = np.radians(beta_deg)
    cos_alpha = np.cos(alpha)
    sin_alpha = np.sin(alpha)
    tan_beta = np.tan(beta)
    
    d1 = (dMi * cos_alpha) + (pixel_yi - pixel_y) * (dC * tan_beta / (pixel_ymax_2)) * sin_alpha

    d_security = d1 - dS
    return d_security

def process_frames(pipeline_d435, pipeline_l515, width_d435, height_d435, width_l515, height_l515):
    alert_triggered = False

    frames_d435 = pipeline_d435.wait_for_frames()
    frames_l515 = pipeline_l515.wait_for_frames()
    depth_frame_d435 = frames_d435.get_depth_frame()
    depth_frame_l515 = frames_l515.get_depth_frame()
    
    if not depth_frame_d435 or not depth_frame_l515:
        return None, None

    cell_width_d435, cell_height_d435 = width_d435 // 28, height_d435 // 28
    cell_width_l515, cell_height_l515 = width_l515 // 28, height_l515 // 28

    depth_colormap_d435 = cv2.applyColorMap(cv2.convertScaleAbs(np.asanyarray(depth_frame_d435.get_data()), alpha=0.03), cv2.COLORMAP_JET)
    depth_colormap_l515 = cv2.applyColorMap(cv2.convertScaleAbs(np.asanyarray(depth_frame_l515.get_data()), alpha=0.03), cv2.COLORMAP_JET)
    width_d435, height_d435 = 848, 480 

    # These values can vary depending on the environment but must be the same ones as in "def find_min_d_security"
    
    for cell_x in range(10, 19):
        for cell_y in range(6, 27):
            cell_center_x_d435, cell_center_y_d435 = get_central_pixel_coordinates(width_d435, height_d435, cell_x, cell_y, cell_width_d435, cell_height_d435)
            cell_center_x_l515, cell_center_y_l515 = get_central_pixel_coordinates(width_l515, height_l515, cell_x, cell_y, cell_width_l515, cell_height_l515)

            cv2.circle(depth_colormap_d435,(cell_center_x_d435, cell_center_y_d435), 3, (0, 0, 255), -1)
            cv2.circle(depth_colormap_l515,(cell_center_x_l515, cell_center_y_l515), 3, (0, 0, 255), -1)


    min_d_security_d435, min_pixel_d435 = find_min_d_security(depth_frame_d435, width_d435, height_d435, cell_width_d435, cell_height_d435, alpha_deg=25, beta_deg=29, pixel_y=240, pixel_ymax_2=240)

    min_d_security_l515, min_pixel_l515 = find_min_d_security(depth_frame_l515, width_l515, height_l515, cell_width_l515, cell_height_l515, alpha_deg=25, beta_deg=22.5, pixel_y=384, pixel_ymax_2=384)

    # print(f"Min d_security D435: {min_d_security_d435}, Pixel: {min_pixel_d435}")
    # print(f"Min d_security L515: {min_d_security_l515}, Pixel: {min_pixel_l515}")

    # Compare the minimal d_security values and take corresponding actions
    if min_d_security_d435 is not None and min_d_security_l515 is not None:
        if abs(min_d_security_d435 - min_d_security_l515) <= 0.15:
            if 0.1 < min_d_security_d435 < 0.5:
                # cv2.circle(depth_colormap_d435, min_pixel_d435, 3, (0, 255, 255), -1)
                print(f"COLLISION: {min_d_security_d435:.2f} meters away at pixel ({min_pixel_d435[0]}, {min_pixel_d435[1]})")
                write_to_file('0')
                time.sleep(0.2)
                write_to_file('')
                alert_triggered = True
            elif 0.51 < min_d_security_d435 < 1.0:
                # cv2.circle(depth_colormap_d435, min_pixel_d435, 3, (255, 0, 0), -1)
                print(f"ALERT: Object at a distance of {min_d_security_d435:.2f} meters away at pixel ({min_pixel_d435[0]}, {min_pixel_d435[1]})")
                write_to_file('6')
                time.sleep(0.2)
                write_to_file('')
                alert_triggered = True
                
    # Only D435 has valid data, take actions based on d_security_d435

    elif min_d_security_d435 is not None:
        if 0.1 < min_d_security_d435 < 0.5:
            # cv2.circle(depth_colormap_d435, min_pixel_d435, 3, (0, 0, 255), -1)
            print(f"COLLISION: {min_d_security_d435:.2f} meters away at pixel ({min_pixel_d435[0]}, {min_pixel_d435[1]})")
            write_to_file('0')
            time.sleep(0.2)
            write_to_file('')
            alert_triggered = True
        elif 0.51 < min_d_security_d435 < 1.0:
            # cv2.circle(depth_colormap_d435, min_pixel_d435, 3, (255, 0, 0), -1)
            print(f"ALERT: Object at a distance of {min_d_security_d435:.2f} meters away at pixel ({min_pixel_d435[0]}, {min_pixel_d435[1]})")
            write_to_file('6')
            time.sleep(0.2)
            write_to_file('')
            alert_triggered = True
        elif 1.01 < min_d_security_d435 < 1.5:
            cv2.circle(depth_colormap_d435, min_pixel_d435, 3, (255, 0, 0), -1)
            play_beep()
            write_to_file('')
            time.sleep(0.2)
            write_to_file('')
            alert_triggered = True

    return depth_colormap_d435, depth_colormap_l515, alert_triggered

def find_min_d_security(depth_frame, width, height, cell_width, cell_height, alpha_deg, beta_deg, pixel_y, pixel_ymax_2):
    min_d_security = None
    min_pixel = None

    
    for cell_x in range(14, 19):
        for cell_y in range(10, 20):
            cell_center_x, cell_center_y = get_central_pixel_coordinates(width, height, cell_x, cell_y, cell_width, cell_height)
            distance_value = depth_frame.get_distance(cell_center_x, cell_center_y)
            
            alpha = np.radians(alpha_deg)
            beta = np.radians(beta_deg)
            cos_alpha = np.cos(alpha)
            sin_alpha = np.sin(alpha)
            tan_beta = np.tan(beta)
            
            dS = 1.35
            min_d = (0.1+dS) / (cos_alpha + (cell_center_y - pixel_y) * (tan_beta / pixel_ymax_2) * sin_alpha)
            
            if distance_value > min_d:
                d_security = calculate_d_security(dS=dS, dMi=distance_value, dC=distance_value, alpha_deg=alpha_deg, beta_deg=beta_deg, pixel_yi=cell_center_y, pixel_y=pixel_y, pixel_ymax_2=pixel_ymax_2)
                
                if min_d_security is None or d_security < min_d_security:
                    min_d_security = d_security
                    min_pixel = (cell_center_x, cell_center_y)
    
    return min_d_security, min_pixel


def main():
    initialize_file()

    # Configure RealSense pipelines
    pipeline_d435 = rs.pipeline()
    config_d435 = rs.config()
    configure_camera_d435(config_d435)
    pipeline_d435.start(config_d435)

    pipeline_l515 = rs.pipeline()
    config_l515 = rs.config()
    configure_camera_l515(config_l515)
    pipeline_l515.start(config_l515)

    width_d435, height_d435 = 848, 480 
    width_l515, height_l515 = 1024, 768 

    # Executor to run process_frames concurrently
    executor = ThreadPoolExecutor(max_workers=2)
    future = executor.submit(process_frames, pipeline_d435, pipeline_l515, width_d435, height_d435, width_l515, height_l515)

    while True:
        try:
            # Get the result from the future processor
            result = future.result()
            
            if result is not None:
                depth_colormap_d435, depth_colormap_l515, alert_triggered = result
                
                # Display depth_colormap_d435 using cv2.imshow
                cv2.imshow('RealSense D435 Depth Map', depth_colormap_d435)
                cv2.imshow('RealSense L515 Depth Map', depth_colormap_l515)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # Reset future for next frame processing
                future = executor.submit(process_frames, pipeline_d435, pipeline_l515, width_d435, height_d435, width_l515, height_l515)
            else:
                # Handle the case when result is None (frames are not available)
                print("Warning: Frames are not available.")
                time.sleep(0.1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Exception occurred: {e}")
            stop_measurements(pipeline_l515, pipeline_d435)
            break

    # Stop the pipelines and close all windows
    stop_measurements(pipeline_l515, pipeline_d435)

if __name__ == "__main__":
    main()
