import os
import csv
import zipfile
import io
from datetime import datetime, timedelta

def generate_mumbai_metro_gtfs(output_zip_path: str):
    print("Generating Mumbai Metro GTFS feed...")

    # 1. Agency.txt
    agencies = [
        {"agency_id": "MMOPL", "agency_name": "Mumbai Metro One Pvt Ltd", "agency_url": "https://www.reliancemumbaimetro.com", "agency_timezone": "Asia/Kolkata", "agency_lang": "en", "agency_phone": "022-30310911"},
        {"agency_id": "MMMOCL", "agency_name": "Maha Mumbai Metro Operation Corp Ltd", "agency_url": "https://www.mmmocl.co.in", "agency_timezone": "Asia/Kolkata", "agency_lang": "en", "agency_phone": "1800-889-0505"},
        {"agency_id": "MMRC", "agency_name": "Mumbai Metro Rail Corp Ltd", "agency_url": "https://www.mmrcl.com", "agency_timezone": "Asia/Kolkata", "agency_lang": "en", "agency_phone": "022-66310900"}
    ]

    # 2. Routes.txt
    routes = [
        {"route_id": "METRO_1", "agency_id": "MMOPL", "route_short_name": "Line 1", "route_long_name": "Blue Line (Versova - Ghatkopar)", "route_type": "1", "route_color": "0072CE", "route_text_color": "FFFFFF"},
        {"route_id": "METRO_2A", "agency_id": "MMMOCL", "route_short_name": "Line 2A", "route_long_name": "Yellow Line (Dahisar East - Andheri West)", "route_type": "1", "route_color": "FFD100", "route_text_color": "000000"},
        {"route_id": "METRO_7", "agency_id": "MMMOCL", "route_short_name": "Line 7", "route_long_name": "Red Line (Dahisar East - Gundavali)", "route_type": "1", "route_color": "ED1C24", "route_text_color": "FFFFFF"},
        {"route_id": "METRO_3", "agency_id": "MMRC", "route_short_name": "Line 3", "route_long_name": "Aqua Line (Aarey JVLR - BKC)", "route_type": "1", "route_color": "00A3E0", "route_text_color": "FFFFFF"}
    ]

    # 3. Stops.txt
    stops_data = [
        # Line 1
        ("MM1_VER", "Versova", 19.1316, 72.8174),
        ("MM1_DNN", "D.N. Nagar", 19.1278, 72.8277),
        ("MM1_AZD", "Azad Nagar", 19.1256, 72.8364),
        ("MM1_ADH", "Andheri Metro", 19.1205, 72.8467),
        ("MM1_WEH", "Western Express Highway", 19.1158, 72.8569),
        ("MM1_CHK", "Chakala (J.B. Nagar)", 19.1114, 72.8654),
        ("MM1_APR", "Airport Road", 19.1087, 72.8732),
        ("MM1_MRN", "Marol Naka", 19.1062, 72.8827),
        ("MM1_SKN", "Saki Naka", 19.0984, 72.8876),
        ("MM1_ASP", "Asalpha", 19.0911, 72.8951),
        ("MM1_JGN", "Jagruti Nagar", 19.0886, 72.9022),
        ("MM1_GHT", "Ghatkopar Metro", 19.0858, 72.9081),
        # Line 2A
        ("MM2_DHE", "Dahisar East", 19.2573, 72.8601),
        ("MM2_AND", "Anand Nagar", 19.2558, 72.8524),
        ("MM2_KND", "Kandarpada", 19.2514, 72.8486),
        ("MM2_MDP", "Mandapeshwar", 19.2443, 72.8471),
        ("MM2_EKS", "Eksar", 19.2366, 72.8465),
        ("MM2_BVW", "Borivali West", 19.2291, 72.8458),
        ("MM2_PHE", "Pahadi Eksar", 19.2195, 72.8449),
        ("MM2_KVW", "Kandivali West", 19.2120, 72.8441),
        ("MM2_DHN", "Dahanukarwadi", 19.2045, 72.8434),
        ("MM2_VAL", "Valnai", 19.1968, 72.8427),
        ("MM2_MLW", "Malad West", 19.1869, 72.8419),
        ("MM2_LML", "Lower Malad", 19.1772, 72.8398),
        ("MM2_PHG", "Pahadi Goregaon", 19.1684, 72.8386),
        ("MM2_GRW", "Goregaon West", 19.1587, 72.8374),
        ("MM2_OSH", "Oshiwara", 19.1492, 72.8361),
        ("MM2_LOS", "Lower Oshiwara", 19.1396, 72.8347),
        ("MM2_ADW", "Andheri West", 19.1278, 72.8277),
        # Line 7
        ("MM7_DHE", "Dahisar East", 19.2573, 72.8601),
        ("MM7_OVR", "Ovaripada", 19.2482, 72.8614),
        ("MM7_NPK", "National Park (Borivali)", 19.2312, 72.8628),
        ("MM7_DVP", "Devipada", 19.2241, 72.8637),
        ("MM7_MGT", "Magathane", 19.2173, 72.8646),
        ("MM7_PSR", "Poisar", 19.2084, 72.8655),
        ("MM7_AKR", "Akurli", 19.2012, 72.8664),
        ("MM7_KRR", "Kurar", 19.1925, 72.8673),
        ("MM7_DND", "Dindoshi", 19.1798, 72.8682),
        ("MM7_ARY", "Aarey", 19.1687, 72.8691),
        ("MM7_GRE", "Goregaon East", 19.1576, 72.8679),
        ("MM7_JGE", "Jogeshwari East", 19.1392, 72.8624),
        ("MM7_MGR", "Mogra", 19.1281, 72.8596),
        ("MM7_GDV", "Gundavali", 19.1158, 72.8569),
        # Line 3
        ("MM3_ARJ", "Aarey JVLR", 19.1384, 72.8802),
        ("MM3_SPZ", "SEEPZ", 19.1276, 72.8791),
        ("MM3_MDC", "MIDC Andheri", 19.1179, 72.8752),
        ("MM3_MRN", "Marol Naka", 19.1062, 72.8827),
        ("MM3_CT2", "CSMIA T2", 19.0961, 72.8745),
        ("MM3_SHR", "Sahar Road", 19.0912, 72.8623),
        ("MM3_CT1", "CSMIA T1", 19.0894, 72.8531),
        ("MM3_STC", "Santacruz Metro", 19.0805, 72.8422),
        ("MM3_VDN", "Vidyanagari", 19.0721, 72.8594),
        ("MM3_BKC", "Bandra Kurla Complex", 19.0652, 72.8687)
    ]

    stops = []
    seen_stop_ids = set()
    for stop_id, name, lat, lon in stops_data:
        if stop_id not in seen_stop_ids:
            stops.append({
                "stop_id": stop_id,
                "stop_name": name,
                "stop_lat": str(lat),
                "stop_lon": str(lon),
                "location_type": "0",
                "wheelchair_boarding": "1" # All Mumbai Metro stations are wheelchair accessible
            })
            seen_stop_ids.add(stop_id)

    # 4. Calendar.txt
    calendar = [
        {"service_id": "ALL_DAYS", "monday": "1", "tuesday": "1", "wednesday": "1", "thursday": "1", "friday": "1", "saturday": "1", "sunday": "1", "start_date": "20260101", "end_date": "20261231"}
    ]

    # 5. Transfers.txt (Interchanges)
    transfers = [
        {"from_stop_id": "MM1_WEH", "to_stop_id": "MM7_GDV", "transfer_type": "2", "min_transfer_time": "270"},
        {"from_stop_id": "MM7_GDV", "to_stop_id": "MM1_WEH", "transfer_type": "2", "min_transfer_time": "270"},
        {"from_stop_id": "MM1_DNN", "to_stop_id": "MM2_ADW", "transfer_type": "2", "min_transfer_time": "120"},
        {"from_stop_id": "MM2_ADW", "to_stop_id": "MM1_DNN", "transfer_type": "2", "min_transfer_time": "120"},
        {"from_stop_id": "MM1_MRN", "to_stop_id": "MM3_MRN", "transfer_type": "2", "min_transfer_time": "180"},
        {"from_stop_id": "MM3_MRN", "to_stop_id": "MM1_MRN", "transfer_type": "2", "min_transfer_time": "180"},
        {"from_stop_id": "MM2_DHE", "to_stop_id": "MM7_DHE", "transfer_type": "2", "min_transfer_time": "120"},
        {"from_stop_id": "MM7_DHE", "to_stop_id": "MM2_DHE", "transfer_type": "2", "min_transfer_time": "120"}
    ]

    # 6. Generate Trips & Stop Times
    lines = [
        ("METRO_1", [s[0] for s in stops_data if s[0].startswith("MM1_")], 0, 18, 4), # 4 min headway, 18 min journey
        ("METRO_2A", [s[0] for s in stops_data if s[0].startswith("MM2_")], 0, 32, 7), # 7 min headway, 32 min journey
        ("METRO_7", [s[0] for s in stops_data if s[0].startswith("MM7_")], 0, 28, 7), # 7 min headway, 28 min journey
        ("METRO_3", [s[0] for s in stops_data if s[0].startswith("MM3_")], 0, 22, 6)  # 6 min headway, 22 min journey
    ]

    trips = []
    stop_times = []

    def format_time(total_seconds):
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    for route_id, stop_list, _, total_min, headway_min in lines:
        for direction_id, current_stops in [(0, stop_list), (1, list(reversed(stop_list)))]:
            num_stops = len(current_stops)
            hop_seconds = (total_min * 60) / (num_stops - 1)

            # Start operating from 05:30 to 23:30 (5.5h to 23.5h)
            start_time_sec = int(5.5 * 3600)
            end_time_sec = int(23.5 * 3600)
            trip_counter = 1

            curr_sec = start_time_sec
            while curr_sec <= end_time_sec:
                trip_id = f"{route_id}_DIR{direction_id}_T{trip_counter:03d}"
                headsign = stops_data[[s[0] for s in stops_data].index(current_stops[-1])][1]

                trips.append({
                    "route_id": route_id,
                    "service_id": "ALL_DAYS",
                    "trip_id": trip_id,
                    "trip_headsign": headsign,
                    "direction_id": str(direction_id)
                })

                # Stop times for this trip
                for idx, st_id in enumerate(current_stops):
                    arr_sec = curr_sec + (idx * hop_seconds)
                    dep_sec = arr_sec + 25 # 25 second dwell time
                    stop_times.append({
                        "trip_id": trip_id,
                        "arrival_time": format_time(arr_sec),
                        "departure_time": format_time(dep_sec),
                        "stop_id": st_id,
                        "stop_sequence": str(idx + 1)
                    })

                curr_sec += headway_min * 60
                trip_counter += 1

    # Write all to ZIP file
    os.makedirs(os.path.dirname(os.path.abspath(output_zip_path)), exist_ok=True)
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        def add_csv(filename, fieldnames, rows):
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
            zipf.writestr(filename, buf.getvalue())

        add_csv("agency.txt", ["agency_id", "agency_name", "agency_url", "agency_timezone", "agency_lang", "agency_phone"], agencies)
        add_csv("routes.txt", ["route_id", "agency_id", "route_short_name", "route_long_name", "route_type", "route_color", "route_text_color"], routes)
        add_csv("stops.txt", ["stop_id", "stop_name", "stop_lat", "stop_lon", "location_type", "wheelchair_boarding"], stops)
        add_csv("calendar.txt", ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"], calendar)
        add_csv("trips.txt", ["route_id", "service_id", "trip_id", "trip_headsign", "direction_id"], trips)
        add_csv("stop_times.txt", ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"], stop_times)
        add_csv("transfers.txt", ["from_stop_id", "to_stop_id", "transfer_type", "min_transfer_time"], transfers)

    print(f"Successfully generated {output_zip_path} with {len(stops)} stops, {len(routes)} routes, and {len(trips)} trips.")

if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "otp", "data", "mumbai-metro.gtfs.zip")
    generate_mumbai_metro_gtfs(out_path)
