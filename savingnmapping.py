def process_frame():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        frame_timestamp = time.time()
        results = model.predict(frame, conf=0.6, iou=0.4)
        annotated_frame = frame.copy()
        
        lat, lon = parse_gps_data(frame_timestamp)
        if lat and lon:
            cv2.putText(
                annotated_frame,
                f"GPS: ({lat:.6f}, {lon:.6f})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, 
                (255, 255, 255),
                3,
            )
        else:
            cv2.putText(
                annotated_frame,
                "GPS: Not Available",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, 
                (0, 0, 255),
                3,
            )
        
        if results[0].masks is not None and len(results[0].masks.data) > 0:
            for mask in results[0].masks.data:
                mask_np = mask.cpu().numpy().astype(np.uint8)
                if mask_np.size == 0:
                    continue
                mask_resized = cv2.resize(mask_np, (frame.shape[1], frame.shape[0]))
                pixels_area = cv2.countNonZero(mask_resized)
                
                distance_m = REFERENCE_DISTANCE
                real_area_cm2 = estimate_real_area(pixels_area, distance_m)
                severity, color = calculate_severity(real_area_cm2)
                
                x, y, w, h = cv2.boundingRect(mask_resized)
                angle = math.atan2(y + h / 2 - frame.shape[0] / 2, x + w / 2 - frame.shape[1] / 2)
                
                if lat is not None and lon is not None:
                    pothole_lat, pothole_lon = adjust_gps_coordinates(lat, lon, distance_m, angle)
                    
                    # Save to database
                    save_to_database(pothole_lat, pothole_lon, severity)
                    
                    # Draw bounding box and annotations
                    cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(
                        annotated_frame,
                        f"Severity: {severity} ({real_area_cm2:.1f} cm^2)",
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, 
                        color,
                        3,
                    )
                    cv2.putText(
                        annotated_frame,
                        f"Location: ({pothole_lat:.6f}, {pothole_lon:.6f})",
                        (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        color,
                        3,
                    )
                    print(f"Detected pothole at coordinates: ({pothole_lat:.6f}, {pothole_lon:.6f})")
                else:
                    print("Skipping pothole detection due to missing GPS data.")
        
        cv2.imshow("Pothole Detection", cv2.resize(annotated_frame, (640, 480)))
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()
