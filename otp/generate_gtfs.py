import csv
import io
import os
import zipfile

def generate_gtfs_packages(output_dir="otp/data"):
    os.makedirs(output_dir, exist_ok=True)

    # 1. MUMBAI SUBURBAN RAIL GTFS
    rail_agencies = [
        {"agency_id": "WR", "agency_name": "Western Railway", "agency_url": "https://wr.indianrailways.gov.in", "agency_timezone": "Asia/Kolkata", "agency_lang": "en"},
        {"agency_id": "CR", "agency_name": "Central Railway", "agency_url": "https://cr.indianrailways.gov.in", "agency_timezone": "Asia/Kolkata", "agency_lang": "en"}
    ]

    rail_routes = [
        {"route_id": "SUB_WESTERN", "agency_id": "WR", "route_short_name": "Western", "route_long_name": "Western Suburban Railway (Churchgate - Virar)", "route_type": "2"},
        {"route_id": "SUB_CENTRAL", "agency_id": "CR", "route_short_name": "Central", "route_long_name": "Central Suburban Railway (CSMT - Kalyan)", "route_type": "2"},
        {"route_id": "SUB_HARBOUR", "agency_id": "CR", "route_short_name": "Harbour", "route_long_name": "Harbour Suburban Railway (CSMT - Panvel)", "route_type": "2"},
    ]

    western_stations = [
        ("CHURCHGATE", "Churchgate", 18.9322, 72.8264),
        ("MARINE_LINES", "Marine Lines", 18.9437, 72.8236),
        ("CHARNI_ROAD", "Charni Road", 18.9518, 72.8188),
        ("GRANT_ROAD", "Grant Road", 18.9631, 72.8162),
        ("MUMBAI_CENTRAL", "Mumbai Central", 18.9696, 72.8194),
        ("MAHALAXMI", "Mahalaxmi", 18.9827, 72.8239),
        ("LOWER_PAREL", "Lower Parel", 18.9953, 72.8306),
        ("PRABHADEVI", "Prabhadevi", 19.0063, 72.8335),
        ("DADAR_WR", "Dadar", 19.0178, 72.8478),
        ("MATUNGA_ROAD", "Matunga Road", 19.0278, 72.8447),
        ("MAHIM", "Mahim Junction", 19.0407, 72.8442),
        ("BANDRA", "Bandra", 19.0544, 72.8402),
        ("KHAR_ROAD", "Khar Road", 19.0694, 72.8396),
        ("SANTACRUZ", "Santacruz", 19.0817, 72.8401),
        ("VILE_PARLE", "Vile Parle", 19.0991, 72.8439),
        ("ANDHERI", "Andheri", 19.1197, 72.8464),
        ("JOGESHWARI", "Jogeshwari", 19.1356, 72.8494),
        ("RAM_MANDIR", "Ram Mandir", 19.1517, 72.8488),
        ("GOREGAON", "Goregaon", 19.1646, 72.8493),
        ("MALAD", "Malad", 19.1866, 72.8486),
        ("KANDIVALI", "Kandivali", 19.2045, 72.8524),
        ("BORIVALI", "Borivali", 19.2290, 72.8574),
        ("DAHISAR", "Dahisar", 19.2501, 72.8593),
        ("MIRA_ROAD", "Mira Road", 19.2814, 72.8559),
        ("BHAYANDAR", "Bhayandar", 19.3122, 72.8526),
        ("NAIGAON", "Naigaon", 19.3524, 72.8466),
        ("VASAI_ROAD", "Vasai Road", 19.3813, 72.8322),
        ("NALLASOPARA", "Nallasopara", 19.4168, 72.8229),
        ("VIRAR", "Virar", 19.4544, 72.8116),
    ]

    central_stations = [
        ("CSMT", "Chhatrapati Shivaji Maharaj Terminus", 18.9401, 72.8354),
        ("MASJID", "Masjid", 18.9525, 72.8383),
        ("SANDHURST_ROAD", "Sandhurst Road", 18.9613, 72.8394),
        ("BYCULLA", "Byculla", 18.9772, 72.8335),
        ("CHINCHPOKLI", "Chinchpokli", 18.9892, 72.8328),
        ("CURREY_ROAD", "Currey Road", 18.9959, 72.8339),
        ("PAREL", "Parel", 19.0068, 72.8378),
        ("DADAR_CR", "Dadar", 19.0178, 72.8478),
        ("MATUNGA", "Matunga", 19.0270, 72.8553),
        ("SION", "Sion", 19.0435, 72.8617),
        ("KURLA", "Kurla", 19.0657, 72.8794),
        ("VIDYAVIHAR", "Vidyavihar", 19.0798, 72.8973),
        ("GHATKOPAR", "Ghatkopar", 19.0860, 72.9090),
        ("VIKHROLI", "Vikhroli", 19.1105, 72.9284),
        ("KANJURMARG", "Kanjurmarg", 19.1303, 72.9377),
        ("BHANDUP", "Bhandup", 19.1438, 72.9392),
        ("NAHUR", "Nahur", 19.1575, 72.9431),
        ("MULUND", "Mulund", 19.1726, 72.9562),
        ("THANE", "Thane", 19.1860, 72.9759),
        ("KALVA", "Kalva", 19.2015, 72.9930),
        ("MUMBRA", "Mumbra", 19.1764, 73.0232),
        ("DIVA", "Diva Junction", 19.1887, 73.0427),
        ("KOPAR", "Kopar", 19.2140, 73.0769),
        ("DOMBIVLI", "Dombivli", 19.2183, 73.0867),
        ("THAKURLI", "Thakurli", 19.2272, 73.1025),
        ("KALYAN", "Kalyan Junction", 19.2367, 73.1303),
    ]

    harbour_stations = [
        ("CSMT_HB", "Chhatrapati Shivaji Maharaj Terminus", 18.9401, 72.8354),
        ("MASJID_HB", "Masjid", 18.9525, 72.8383),
        ("SANDHURST_ROAD_HB", "Sandhurst Road", 18.9613, 72.8394),
        ("DOCKYARD_ROAD", "Dockyard Road", 18.9675, 72.8436),
        ("REAY_ROAD", "Reay Road", 18.9772, 72.8467),
        ("COTTON_GREEN", "Cotton Green", 18.9867, 72.8492),
        ("SEWRI", "Sewri", 19.0006, 72.8550),
        ("VADALA_ROAD", "Vadala Road", 19.0167, 72.8583),
        ("GTB_NAGAR", "Guru Tegh Bahadur Nagar", 19.0358, 72.8631),
        ("CHUNABHATTI", "Chunabhatti", 19.0494, 72.8719),
        ("KURLA_HB", "Kurla", 19.0657, 72.8794),
        ("TILAK_NAGAR", "Tilak Nagar", 19.0683, 72.8931),
        ("CHEMBUR", "Chembur", 19.0625, 72.9014),
        ("GOVANDI", "Govandi", 19.0567, 72.9150),
        ("MANKHURD", "Mankhurd", 19.0489, 72.9317),
        ("VASHI", "Vashi", 19.0767, 72.9983),
        ("NERUL", "Nerul", 19.0347, 73.0183),
        ("PANVEL", "Panvel", 18.9889, 73.1111),
    ]

    rail_stops_dict = {}
    for st_list in [western_stations, central_stations, harbour_stations]:
        for sid, sname, slat, slon in st_list:
            rail_stops_dict[sid] = {"stop_id": sid, "stop_name": sname, "stop_lat": slat, "stop_lon": slon, "wheelchair_boarding": 1}

    def build_trips_and_times(route_id, stations, headway_mins, speed_mins_per_stop, start_hour=4, end_hour=24):
        trips = []
        stop_times = []
        service_id = "DAILY"

        # Direction 0: stations[0] -> stations[-1]
        # Direction 1: stations[-1] -> stations[0]
        trip_num = 1
        for start_m in range(start_hour * 60, end_hour * 60, headway_mins):
            for direction_id, seq in [(0, stations), (1, list(reversed(stations)))]:
                trip_id = f"{route_id}_{direction_id}_{trip_num:04d}"
                headsign = seq[-1][1]
                trips.append({
                    "route_id": route_id,
                    "service_id": service_id,
                    "trip_id": trip_id,
                    "trip_headsign": headsign,
                    "direction_id": direction_id
                })

                cur_time = start_m
                for idx, (sid, sname, slat, slon) in enumerate(seq):
                    arr_h = cur_time // 60
                    arr_m = cur_time % 60
                    time_str = f"{arr_h:02d}:{arr_m:02d}:00"
                    stop_times.append({
                        "trip_id": trip_id,
                        "arrival_time": time_str,
                        "departure_time": time_str,
                        "stop_id": sid,
                        "stop_sequence": idx + 1,
                        "timepoint": 1
                    })
                    cur_time += speed_mins_per_stop
                trip_num += 1

        return trips, stop_times

    wr_trips, wr_times = build_trips_and_times("SUB_WESTERN", western_stations, headway_mins=5, speed_mins_per_stop=3)
    cr_trips, cr_times = build_trips_and_times("SUB_CENTRAL", central_stations, headway_mins=5, speed_mins_per_stop=3)
    hb_trips, hb_times = build_trips_and_times("SUB_HARBOUR", harbour_stations, headway_mins=8, speed_mins_per_stop=3)

    all_rail_trips = wr_trips + cr_trips + hb_trips
    all_rail_times = wr_times + cr_times + hb_times

    rail_calendar = [{
        "service_id": "DAILY",
        "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1, "saturday": 1, "sunday": 1,
        "start_date": "20260101", "end_date": "20271231"
    }]

    rail_feed_info = [{
        "feed_publisher_name": "Indian Railways (Suburban Mumbai Feed)",
        "feed_publisher_url": "https://wr.indianrailways.gov.in",
        "feed_lang": "en",
        "feed_start_date": "20260101",
        "feed_end_date": "20271231"
    }]

    # Save mumbai-suburban-rail.gtfs.zip
    def save_zip(filename, agencies, routes, stops, trips, times, calendar, feed_info):
        zip_path = os.path.join(output_dir, filename)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            def write_csv(arcname, fieldnames, rows):
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
                z.writestr(arcname, buf.getvalue().encode("utf-8"))

            write_csv("agency.txt", list(agencies[0].keys()), agencies)
            write_csv("routes.txt", list(routes[0].keys()), routes)
            write_csv("stops.txt", ["stop_id", "stop_name", "stop_lat", "stop_lon", "wheelchair_boarding"], list(stops.values()))
            write_csv("trips.txt", list(trips[0].keys()), trips)
            write_csv("stop_times.txt", list(times[0].keys()), times)
            write_csv("calendar.txt", list(calendar[0].keys()), calendar)
            write_csv("feed_info.txt", list(feed_info[0].keys()), feed_info)
        print(f"Generated {zip_path} with {len(routes)} routes, {len(stops)} stops, {len(trips)} trips.")

    save_zip("mumbai-suburban-rail.gtfs.zip", rail_agencies, rail_routes, rail_stops_dict, all_rail_trips, all_rail_times, rail_calendar, rail_feed_info)

    # 2. MUMBAI METRO GTFS
    metro_agencies = [
        {"agency_id": "MMOPL", "agency_name": "Mumbai Metro One (Reliance Infra)", "agency_url": "https://reliancemumbaimetro.com", "agency_timezone": "Asia/Kolkata", "agency_lang": "en"},
        {"agency_id": "MMMOCL", "agency_name": "Maha Mumbai Metro Operation Corp", "agency_url": "https://mmmocl.co.in", "agency_timezone": "Asia/Kolkata", "agency_lang": "en"},
        {"agency_id": "MMRCL", "agency_name": "Mumbai Metro Rail Corporation (Metro 3)", "agency_url": "https://mmrcl.com", "agency_timezone": "Asia/Kolkata", "agency_lang": "en"}
    ]

    metro_routes = [
        {"route_id": "METRO_1", "agency_id": "MMOPL", "route_short_name": "Line 1", "route_long_name": "Blue Line (Versova - Ghatkopar)", "route_type": "1"},
        {"route_id": "METRO_2A", "agency_id": "MMMOCL", "route_short_name": "Line 2A", "route_long_name": "Yellow Line (Dahisar East - D.N. Nagar)", "route_type": "1"},
        {"route_id": "METRO_7", "agency_id": "MMMOCL", "route_short_name": "Line 7", "route_long_name": "Red Line (Dahisar East - Gundavali)", "route_type": "1"},
        {"route_id": "METRO_3", "agency_id": "MMRCL", "route_short_name": "Line 3", "route_long_name": "Aqua Line (Aarey JVLR - BKC)", "route_type": "1"},
    ]

    m1_stations = [
        ("M1_VERSOVA", "Versova", 19.1378, 72.8135),
        ("M1_DN_NAGAR", "D.N. Nagar", 19.1256, 72.8290),
        ("M1_AZAD_NAGAR", "Azad Nagar", 19.1245, 72.8364),
        ("M1_ANDHERI", "Andheri", 19.1197, 72.8464),
        ("M1_WEH", "Western Express Highway", 19.1171, 72.8561),
        ("M1_CHAKALA", "Chakala (J.B. Nagar)", 19.1114, 72.8653),
        ("M1_AIRPORT_RD", "Airport Road", 19.1086, 72.8744),
        ("M1_MAROL_NAKA", "Marol Naka", 19.1072, 72.8833),
        ("M1_SAKI_NAKA", "Saki Naka", 19.1028, 72.8878),
        ("M1_ASALPHA", "Asalpha", 19.0967, 72.8944),
        ("M1_JAGRUTI_NAGAR", "Jagruti Nagar", 19.0911, 72.9028),
        ("M1_GHATKOPAR", "Ghatkopar", 19.0860, 72.9090),
    ]

    m2a_stations = [
        ("M2A_DAHISAR_E", "Dahisar East", 19.2558, 72.8683),
        ("M2A_ANAND_NAGAR", "Anand Nagar", 19.2530, 72.8570),
        ("M2A_KANDARPADA", "Kandarpada", 19.2460, 72.8520),
        ("M2A_MANDAPESHWAR", "Mandapeshwar", 19.2380, 72.8500),
        ("M2A_BORIVALI_W", "Borivali West", 19.2310, 72.8480),
        ("M2A_PAHADI_EKSAR", "Pahadi Eksar", 19.2220, 72.8460),
        ("M2A_KANDIVALI_W", "Kandivali West", 19.2120, 72.8440),
        ("M2A_DAHANUKARWADI", "Dahanukarwadi", 19.2050, 72.8430),
        ("M2A_VALNAI", "Valnai", 19.1960, 72.8420),
        ("M2A_MALAD_W", "Malad West", 19.1870, 72.8410),
        ("M2A_LOWER_MALAD", "Lower Malad", 19.1780, 72.8400),
        ("M2A_BANGUR_NAGAR", "Bangur Nagar", 19.1690, 72.8390),
        ("M2A_GOREGAON_W", "Goregaon West", 19.1600, 72.8380),
        ("M2A_OSHIVARA", "Oshiwara", 19.1480, 72.8350),
        ("M2A_LOWER_OSHIVARA", "Lower Oshiwara", 19.1390, 72.8320),
        ("M2A_DN_NAGAR", "D.N. Nagar", 19.1256, 72.8290),
    ]

    m7_stations = [
        ("M7_DAHISAR_E", "Dahisar East", 19.2558, 72.8683),
        ("M7_OWALE", "Ovaripada", 19.2480, 72.8670),
        ("M7_NATIONAL_PARK", "National Park (Borivali E)", 19.2290, 72.8620),
        ("M7_DEVIPADA", "Devipada", 19.2190, 72.8610),
        ("M7_MAGATHANE", "Magathane", 19.2100, 72.8600),
        ("M7_POISAR", "Poisar", 19.2020, 72.8590),
        ("M7_AKURLI", "Akurli", 19.1950, 72.8580),
        ("M7_KURAR", "Kurar", 19.1860, 72.8570),
        ("M7_DINDOSHI", "Dindoshi", 19.1760, 72.8560),
        ("M7_AAR_COLONY", "Aarey", 19.1630, 72.8550),
        ("M7_GOREGAON_E", "Goregaon East", 19.1530, 72.8540),
        ("M7_JOGESHWARI_E", "Jogeshwari East", 19.1350, 72.8540),
        ("M7_MOGRA", "Mogra", 19.1250, 72.8550),
        ("M7_GUNDAVALI", "Gundavali", 19.1171, 72.8561),
    ]

    m3_stations = [
        ("M3_AAREY", "Aarey JVLR", 19.1450, 72.8750),
        ("M3_SEEPZ", "SEEPZ", 19.1300, 72.8800),
        ("M3_MIDC", "MIDC Andheri", 19.1200, 72.8750),
        ("M3_MAROL", "Marol Naka", 19.1072, 72.8833),
        ("M3_CSMIA_T2", "CSMIA International Airport T2", 19.0970, 72.8740),
        ("M3_SAHAR", "Sahar Road", 19.0990, 72.8620),
        ("M3_CSMIA_T1", "CSMIA Domestic Airport T1", 19.0910, 72.8520),
        ("M3_SANTACRUZ", "Santacruz Metro", 19.0810, 72.8500),
        ("M3_BANDRA_COLONY", "Bandra Colony", 19.0710, 72.8550),
        ("M3_BKC", "Bandra Kurla Complex", 19.0660, 72.8687),
    ]

    metro_stops_dict = {}
    for st_list in [m1_stations, m2a_stations, m7_stations, m3_stations]:
        for sid, sname, slat, slon in st_list:
            metro_stops_dict[sid] = {"stop_id": sid, "stop_name": sname, "stop_lat": slat, "stop_lon": slon, "wheelchair_boarding": 1}

    m1_trips, m1_times = build_trips_and_times("METRO_1", m1_stations, headway_mins=5, speed_mins_per_stop=2)
    m2a_trips, m2a_times = build_trips_and_times("METRO_2A", m2a_stations, headway_mins=7, speed_mins_per_stop=2)
    m7_trips, m7_times = build_trips_and_times("METRO_7", m7_stations, headway_mins=7, speed_mins_per_stop=2)
    m3_trips, m3_times = build_trips_and_times("METRO_3", m3_stations, headway_mins=8, speed_mins_per_stop=2)

    all_metro_trips = m1_trips + m2a_trips + m7_trips + m3_trips
    all_metro_times = m1_times + m2a_times + m7_times + m3_times

    metro_calendar = [{
        "service_id": "DAILY",
        "monday": 1, "tuesday": 1, "wednesday": 1, "thursday": 1, "friday": 1, "saturday": 1, "sunday": 1,
        "start_date": "20260101", "end_date": "20271231"
    }]

    metro_feed_info = [{
        "feed_publisher_name": "Maha Mumbai Metro & MMOPL",
        "feed_publisher_url": "https://mmmocl.co.in",
        "feed_lang": "en",
        "feed_start_date": "20260101",
        "feed_end_date": "20271231"
    }]

    save_zip("mumbai-metro.gtfs.zip", metro_agencies, metro_routes, metro_stops_dict, all_metro_trips, all_metro_times, metro_calendar, metro_feed_info)

if __name__ == "__main__":
    generate_gtfs_packages("otp/data")
