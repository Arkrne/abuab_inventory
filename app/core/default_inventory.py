from typing import Dict, List


ESSENTIAL_ITEMS: List[str] = [
    "Motor oil (Conventional)",
    "Motor oil (Synthetic & Semi-Synthetic)",
    "Transmission fluid (Automatic & Manual)",
    "Brake fluid (DOT 3 & DOT 4)",
    "Power steering fluid",
    "Engine coolant / Antifreeze",
    "Windshield washer fluid",
    "Gear oil / Differential fluid",
    "Grease (Lithium, multi-purpose, wheel bearing)",
    "Penetrating oil (e.g., WD-40)",
    "Carburetor & choke cleaner",
    "Fuel injector cleaner",
    "Engine degreaser",
    "Radiator flush & sealer",
    "Starting fluid",
    "Oil filters (Various sizes for major makes/models)",
    "Engine air filters",
    "Cabin air filters",
    "Fuel filters",
    "Transmission filters",
    "Car batteries (Lead-acid and AGM)",
    "Battery terminals & cables",
    "Jumper cables",
    "Spark plugs",
    "Ignition coils & spark plug wires",
    "Headlight bulbs (Halogen, LED, HID)",
    "Taillight & brake light bulbs",
    "Turn signal & interior bulbs",
    "Fuses (Blade style, mini, and maxi)",
    "Relays & flashers",
    "Alternators (Common models)",
    "Starter motors (Common models)",
    "Electrical tape & heat shrink tubing",
    "Wire connectors & terminals",
    "Zip ties",
    "Brake pads (Ceramic and semi-metallic)",
    "Brake rotors/discs",
    "Brake calipers",
    "Brake shoes (For drum brakes)",
    "Shock absorbers",
    "MacPherson struts",
    "Tie rod ends (Inner and outer)",
    "Ball joints",
    "Wheel bearings & hub assemblies",
    "Sway bar links & bushings",
    "Serpentine belts / Drive belts",
    "Timing belts",
    "V-belts",
    "Radiator hoses (Upper and lower)",
    "Heater hoses",
    "Fuel lines & vacuum hoses (Sold by the foot)",
    "Hose clamps (Assorted sizes)",
    "Thermostats & gaskets",
    "Radiator caps",
    "Water pumps",
    "Windshield wiper blades (Assorted lengths)",
    "Car wash soap & shampoo",
    "Car wax & synthetic paint sealants",
    "Polish & rubbing compound",
    "Microfiber towels & wash mitts",
    "Tire shine & wheel cleaner",
    "Glass cleaner (Automotive specific)",
    "Scratch repair kits",
    "Touch-up paint & clear coat spray",
    "Bumper clips & plastic fasteners",
    "Side view mirrors (Universal and direct-fit)",
    "License plate frames & mounting hardware",
    "Floor mats (Rubber all-weather and carpet)",
    "Seat covers",
    "Steering wheel covers",
    "Air fresheners (Trees, vent clips, sprays)",
    "Phone mounts & holders",
    "USB car chargers & adapters",
    "Dashboard protectant (e.g., Armor All)",
    "Upholstery & carpet cleaner",
    "Sunshades / Windshield reflectors",
    "Emergency warning triangles & road flares",
    "Hydraulic floor jacks",
    "Jack stands (2-ton, 3-ton)",
    "Socket and ratchet sets (Metric & SAE)",
    "Wrenches (Combination and adjustable)",
    "Screwdriver sets",
    "Pliers (Slip-joint, needle-nose, locking)",
    "Oil filter wrenches / Pliers",
    "Tire pressure gauges",
    "OBD-II diagnostic scanners",
    "Digital multimeters",
    "Funnels",
    "Oil drain pans",
    "Mechanic gloves (Disposable nitrile and heavy-duty)",
    "Tire plug/patch kits",
    "Emergency tire sealant (e.g., Fix-a-Flat)",
    "Portable 12V air compressors / Tire inflators",
    "Valve stems, cores, and caps",
    "Lug nuts & wheel studs",
    "Wheel locks",
    "Lug wrenches / 4-way tire irons",
    "Tire tread depth gauges",
    "Wheel chocks",
    "Scissor jacks / Spare tire jacks",
]


CATEGORY_GROUPS: Dict[str, range] = {
    "Fluids & Chemicals": range(1, 16),
    "Filters": range(16, 21),
    "Electrical & Ignition": range(21, 36),
    "Brakes & Suspension": range(36, 46),
    "Belts, Hoses & Cooling": range(46, 56),
    "Exterior, Body & Cleaning": range(56, 68),
    "Interior & Accessories": range(68, 78),
    "Tools & Shop Equipment": range(78, 91),
    "Tires & Wheel Repair": range(91, 101),
}


# Tag hints are used to generate deterministic, product-relevant stock images.
ITEM_IMAGE_TAGS: Dict[str, str] = {
    "motor oil": "motor-oil,car-engine",
    "transmission fluid": "transmission-fluid,car-repair",
    "brake fluid": "brake-fluid,car-brake",
    "power steering": "power-steering,car-engine",
    "coolant": "engine-coolant,radiator",
    "antifreeze": "engine-coolant,radiator",
    "washer fluid": "windshield-washer,car",
    "gear oil": "gear-oil,automotive",
    "grease": "automotive-grease,mechanic",
    "penetrating oil": "wd40,toolbox",
    "carburetor": "carburetor,engine-repair",
    "injector": "fuel-injector,engine",
    "degreaser": "engine-cleaner,car-detailing",
    "radiator": "car-radiator,cooling-system",
    "starting fluid": "engine-start,automotive",
    "filter": "car-filter,auto-parts",
    "battery": "car-battery,automotive",
    "spark plug": "spark-plug,engine",
    "ignition": "ignition-coil,spark-plug",
    "headlight": "car-headlight,auto-light",
    "taillight": "car-tail-light,auto-light",
    "bulb": "automotive-bulb,car-light",
    "fuses": "automotive-fuse,electrical",
    "relays": "automotive-relay,electrical",
    "alternator": "alternator,car-engine",
    "starter": "starter-motor,car-engine",
    "brake pads": "brake-pads,car-brake",
    "rotors": "brake-rotor,car-brake",
    "calipers": "brake-caliper,car-brake",
    "brake shoes": "drum-brake,car-brake",
    "shock": "shock-absorber,suspension",
    "struts": "macpherson-strut,suspension",
    "tie rod": "tie-rod,suspension",
    "ball joint": "ball-joint,suspension",
    "wheel bearing": "wheel-bearing,hub",
    "sway bar": "sway-bar-link,suspension",
    "serpentine": "serpentine-belt,engine-belt",
    "timing belt": "timing-belt,engine",
    "v-belts": "v-belt,engine-belt",
    "hose": "radiator-hose,engine",
    "thermostat": "car-thermostat,cooling-system",
    "water pump": "water-pump,engine",
    "wiper": "windshield-wiper,car",
    "car wash": "car-wash,detailing",
    "wax": "car-wax,detailing",
    "polish": "car-polish,detailing",
    "microfiber": "microfiber-towel,car-detailing",
    "tire shine": "tire-shine,car-wheel",
    "glass cleaner": "car-glass-cleaner,windshield",
    "scratch": "scratch-repair,car-paint",
    "touch-up paint": "car-paint,auto-body",
    "bumper clips": "bumper-clips,auto-body",
    "side view mirrors": "car-side-mirror,auto-body",
    "license plate": "license-plate-frame,car",
    "floor mats": "car-floor-mat,interior",
    "seat covers": "car-seat-cover,interior",
    "steering wheel": "steering-wheel-cover,interior",
    "air fresheners": "car-air-freshener,interior",
    "phone mounts": "car-phone-mount,dashboard",
    "usb": "car-usb-charger,interior",
    "dashboard": "car-dashboard,interior",
    "upholstery": "car-upholstery-cleaner,interior",
    "sunshades": "car-sunshade,windshield",
    "warning triangles": "road-warning-triangle,emergency",
    "jacks": "hydraulic-jack,garage",
    "jack stands": "jack-stands,garage",
    "socket": "socket-set,tools",
    "wrenches": "wrench-set,tools",
    "screwdriver": "screwdriver-set,tools",
    "pliers": "pliers,tools",
    "pressure gauges": "tire-pressure-gauge,tools",
    "obd": "obd2-scanner,diagnostic",
    "multimeters": "digital-multimeter,electrical",
    "funnels": "oil-funnel,garage",
    "drain pans": "oil-drain-pan,garage",
    "gloves": "mechanic-gloves,garage",
    "tire": "tire-repair,car-wheel",
    "valve": "tire-valve-stem,car-wheel",
    "lug": "lug-nuts,car-wheel",
    "wheel locks": "wheel-locks,car-wheel",
    "wheel chocks": "wheel-chocks,garage",
    "scissor jacks": "scissor-jack,car-wheel",
}


CATEGORY_IMAGE_TAGS: Dict[str, str] = {
    "Fluids & Chemicals": "auto-fluids,car-maintenance",
    "Filters": "automotive-filter,auto-parts",
    "Electrical & Ignition": "car-electrical,ignition-system",
    "Brakes & Suspension": "car-brake,suspension",
    "Belts, Hoses & Cooling": "car-engine,cooling-system",
    "Exterior, Body & Cleaning": "car-detailing,auto-body",
    "Interior & Accessories": "car-interior,accessories",
    "Tools & Shop Equipment": "mechanic-tools,garage",
    "Tires & Wheel Repair": "car-tire,wheel-repair",
}


def build_product_image_url(name: str, category: str, item_number: int) -> str:
    lowered_name = name.lower()
    tag_string = ""

    for phrase, tags in ITEM_IMAGE_TAGS.items():
        if phrase in lowered_name:
            tag_string = tags
            break

    if not tag_string:
        tag_string = CATEGORY_IMAGE_TAGS.get(category, "auto-parts,car-repair")

    # loremflickr + lock gives a stable image for each item index.
    return f"https://loremflickr.com/320/220/{tag_string}?lock={item_number}"


def _category_for_index(item_number: int) -> str:
    for category, index_range in CATEGORY_GROUPS.items():
        if item_number in index_range:
            return category
    return "General"


def build_essential_products() -> List[Dict[str, object]]:
    products: List[Dict[str, object]] = []

    for idx, name in enumerate(ESSENTIAL_ITEMS, start=1):
        category = _category_for_index(idx)
        products.append(
            {
                "sku": f"ESS-{idx:03d}",
                "name": name,
                "category": category,
                "image_url": build_product_image_url(name, category, idx),
                "stock_quantity": 20,
                "price": round(149 + (idx * 17.5), 2),
            }
        )

    return products
