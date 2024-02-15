import os
import xml.etree.ElementTree as ET

# Function to extract data from XML
def process_xml_file(xml_file):
    print(f"Processing XML file: {xml_file}")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract animation ID and event type from XML file name
    xml_filename = os.path.splitext(os.path.basename(xml_file))[0]
    parts = xml_filename.split('_')
    animation_id = parts[1]
    event_type = parts[-1].split('.')[0]  # Exclude the file extension
    print(f"{xml_file} Data Found:")
    print(f"AnimationID = {animation_id}")
    print(f"EventsType = {event_type}")

    # Extract event data from XML based on event type
    events = []
    if event_type in ["se", "effect", "facialmotion", "flags"]:
        if event_type == "facialmotion":
            for seq in root.findall(".//FacialMotionTrack"):
                for event in seq.findall(".//Seq"):
                    frame = int(float(event.get("StartTime")) * 30) + 1
                    event_name = f"facialmotion {event.get('AnimationNo')}"
                    events.append((frame, event_name))
                    print(f"Processed {event_name} ({frame}) ({event.get('StartTime')}s)")
        else:
            for seq in root.findall(f".//{event_type.capitalize()}Track"):
                for event in seq.findall(".//Seq"):
                    frame = int(float(event.get("StartTime")) * 30) + 1
                    if event_type == "se":
                        event_name = f"se {event.get('EventName')}"
                    elif event_type == "effect":
                        event_name = f"effect {event.get('EffNo')}"
                    elif event_type == "flags":
                        event_name = f"flag {event.get('Flag0')}"
                    else:
                        event_name = ""
                    events.append((frame, event_name))
                    print(f"Processed {event_name} ({frame}) ({event.get('StartTime')}s)")
    else:
        print(f"Unknown event type: {event_type}")
        return animation_id, []

    print(f"Finished processing {xml_file}\n")
    return animation_id, events

# Process all XML files in the directory
xml_files = [f for f in os.listdir('.') if f.endswith('.xml')]

# Dictionary to store events for each animation ID
animation_events = {}

for xml_file in xml_files:
    animation_id, events = process_xml_file(xml_file)
    if animation_id not in animation_events:
        animation_events[animation_id] = []
    animation_events[animation_id].extend(events)
    print(f"Processed {len(events)} events from {xml_file}\n")

# Write to QCI file
with open("events.QCI", 'w') as qci_file:
    for animation_id, events in animation_events.items():
        # Sort events by event type first, then by frame
        events.sort(key=lambda x: (x[1].split()[0], x[0]))
        qci_file.write(f"$Sequence \"{animation_id}\" {{\n")
        current_event_type = None
        for frame, event_name in events:
            event_type = event_name.split()[0]
            if current_event_type != event_type:
                if current_event_type is not None:
                    qci_file.write("\n")
                current_event_type = event_type
            qci_file.write(f"\t{{ event 1100 {frame} \"{event_name}\" }}\n")
        qci_file.write("}\n")

print("Finished writing events.QCI")
