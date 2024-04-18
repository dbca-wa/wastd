SOURCE_DEFAULT = "direct"
SOURCE_CHOICES = (
    (SOURCE_DEFAULT, "Direct entry"),
    ("paper", "Paper data sheet"),
    ("odk", "OpenDataKit mobile data capture"),
    ("wamtram", "WAMTRAM 2 tagging DB"),
    ("ntp-exmouth", "NTP Access DB Exmouth"),
    ("ntp-broome", "NTP Access DB Broome"),
    ("cet", "Cetacean strandings DB"),
    ("pin", "Pinniped strandings DB"),
    ("reconstructed", "Reconstructed automatically"),
)

SIGHTING_STATUS_CHOICES = (
    ("na", "Unidentified"),
    ("new", "Initial sighting"),
    ("resighting", "Resighting"),
    ("remigrant", "Remigrant"),
)

BODY_PART_DEFAULT = "whole"
TURTLE_BODY_PART_CHOICES = (
    ("head", "Head"),
    ("eyes", "Eyes"),
    ("neck", "Neck"),
    ("plastron", "Plastron"),
    ("carapace", "Carapace"),
    ("internals", "Internal organs"),
    ("cloaca", "Cloaca"),
    ("tail", "Tail"),
    ("flipper-front-left-1", "Front left flipper, 1st scale from body"),
    ("flipper-front-left-2", "Front left flipper, 2nd scale from body"),
    ("flipper-front-left-3", "Front left flipper, 3rd scale from body"),
    ("flipper-front-left", "Front left flipper"),
    ("flipper-front-right-1", "Front right flipper, 1st scale from body"),
    ("flipper-front-right-2", "Front right flipper, 2nd scale from body"),
    ("flipper-front-right-3", "Front right flipper, 3rd scale from body"),
    ("flipper-front-right", "Front right flipper"),
    ("flipper-rear-left", "Fear left flipper"),
    ("flipper-rear-right", "Fear right flipper"),
    ("shoulder-left", "Left shoulder"),
    ("shoulder-right", "Right shoulder"),
    (BODY_PART_DEFAULT, "Whole turtle"),
    ("other", "Other"),
)

TAG_TYPE_DEFAULT = "flipper-tag"
TAG_TYPE_CHOICES = (
    (TAG_TYPE_DEFAULT, "Flipper tag"),
    ("tag-scar", "Tag scar"),
    ("pit-tag", "PIT tag"),
    ("sat-tag", "Satellite relay data logger"),  # SRDL
    ("blood-sample", "Blood sample"),
    ("biopsy-sample", "Biopsy sample"),
    ("stomach-content-sample", "Stomach content sample"),
    ("physical-sample", "Physical sample"),
    ("egg-sample", "Egg sample"),
    ("qld-monel-a-flipper-tag", "QLD Monel Series A flipper tag"),  # TRT_IDENTIFICATION_TYPES A
    ("qld-titanium-k-flipper-tag", "QLD Titanium Series K flipper tag"),  # TRT_IDENTIFICATION_TYPES K
    ("qld-titanium-t-flipper-tag", "QLD Titanium Series T flipper tag"),  # TRT_IDENTIFICATION_TYPES T
    ("acoustic-tag", "Acoustic tag"),  # Acoustic
    ("commonwealth-titanium-flipper-tag", "Commonwealth titanium flipper tag (old db value)"),  # CA cmlth
    ("cmlth-titanium-flipper-tag", "Commonwealth titanium flipper tag"),  # CA cmlth
    ("cayman-juvenile-tag", "Cayman juvenile tag"),  # CT
    ("hawaii-inconel-flipper-tag", "Hawaii Inst Mar Biol Inconel tag"),  # I
    ("ptt", "Platform Transmitter Terminal (PTT)"),  # PTT
    ("rototag", "RotoTag"),  # SFU/FIU
    ("narangebub-nickname", "Narangebup rehab informal name"),  # RREC
    ("aqwa-nickname", "AQWA informal name"),  # UWW, UnderWater World
    ("atlantis-nickname", "Atlantis informal name"),  # ATLANTIS
    ("wa-museum-reptile-registration-number", "WA Museum Natural History Reptiles Catalogue Registration Number (old db value)"),  # WAMusR
    ("wam-reptile-registration-number", "WA Museum Natural History Reptiles Catalogue Registration Number"),  # WAMusR
    ("genetic-tag", "Genetic ID sequence"),
    ("other", "Other"),
)

TAG_STATUS_DEFAULT = "resighted"
TAG_STATUS_APPLIED_NEW = "applied-new"
TAG_STATUS_CHOICES = (  # TRT_TAG_STATES
    ("ordered", "Ordered from manufacturer"),
    ("produced", "Produced by manufacturer"),
    ("delivered", "Delivered to HQ"),
    ("allocated", "Allocated to field team"),
    (TAG_STATUS_APPLIED_NEW, "Applied new"),  # A1, AE
    (TAG_STATUS_DEFAULT, "Re-sighted associated with animal"),  # OX, P, P_OK, RQ, P_ED
    ("reclinched", "Re-sighted and reclinched on animal"),  # RC
    ("removed", "Taken off animal"),  # OO, R
    ("found", "Found detached"),
    ("returned", "Returned to HQ"),
    ("decommissioned", "Decommissioned"),
    ("destroyed", "Destroyed"),
    ("observed", "Observed in any other context, see comments"),
)

TAG_STATUS_RESIGHTED = ("resighted", "reclinched", "removed")
TAG_STATUS_ON_ANIMAL = (TAG_STATUS_APPLIED_NEW, TAG_STATUS_RESIGHTED)

NEST_TAG_STATUS_CHOICES = (
    (TAG_STATUS_APPLIED_NEW, "Applied new"),
    (TAG_STATUS_DEFAULT, "Re-sighted associated with nest"),
)


NA_VALUE = "na"
NA = ((NA_VALUE, "Not applicable"),)

TAXON_CHOICES_DEFAULT = "Cheloniidae"
TAXON_CHOICES = NA + (
    (TAXON_CHOICES_DEFAULT, "Marine turtles"),
    ("Cetacea", "Whales and Dolphins"),
    ("Pinnipedia", "Seals"),
    ("Sirenia", "Dugongs"),
    ("Elasmobranchii", "Sharks and Rays"),
    ("Hydrophiinae", "Sea snakes and kraits"),
)

TURTLE_SPECIES_DEFAULT = "cheloniidae-fam"
TURTLE_SPECIES_CHOICES = (
    ("natator-depressus", "Natator depressus (Flatback turtle)"),
    ("chelonia-mydas", "Chelonia mydas (Green turtle)"),
    ("eretmochelys-imbricata", "Eretmochelys imbricata (Hawksbill turtle)"),
    ("caretta-caretta", "Caretta caretta (Loggerhead turtle)"),
    ("lepidochelys-olivacea", "Lepidochelys olivacea (Olive ridley turtle)"),
    ("dermochelys-coriacea", "Dermochelys coriacea (Leatherback turtle)"),
    ("chelonia-mydas-agassazzi", "Chelonia mydas agassazzi (Black turtle or East Pacific Green)"),
    ("test-turtle", "Test/training turtle"),
    (TURTLE_SPECIES_DEFAULT, "Cheloniidae (Unidentified turtle)"),
    # Caretta caretta x Chelonia mydas (Hybrid turtle)
    # Chelonia mydas x Eretmochelys imbricata (Hybrid turtle)
    # Natator depressus x Caretta caretta (Hybrid turtle)
    # Natator depressus x Chelonia mydas (Hybrid turtle)
)
CETACEAN_SPECIES_CHOICES = (
    # dolphins
    ("delphinus-delphis", "Delphinus delphis (Short-beaked common dolphin)"),
    ("grampus-griseus", "Grampus griseus (Risso's dolphin)"),
    ("lagenodelphis-hosei", "Lagenodelphis hosei (Fraser's dolphin)"),
    ("lagenorhynchus-obscurus", "Lagenorhynchus obscurus (Dusky dolphin)"),
    ("orcaella-heinsohni", "Orcaella heinsohni (Australian snubfin dolphin)"),
    ("sousa-sahulensis", "Sousa sahulensis (Australian humpback dolphin)"),
    ("sousa-chinensis", "Sousa chinensis (Chinese white dolphin)"),
    ("stenella-attenuata", "Stenella attenuata (Pantropical spotted dolphin)"),
    ("stenella-coeruleoalba", "Stenella coeruleoalba (Striped dolphin)"),
    ("stenella-longirostris", "Stenella longirostris (Spinner dolphin)"),
    ("stenella-sp", "Stenella sp. (Unidentified spotted dolphin)"),
    ("steno-bredanensis", "Steno bredanensis (Rough-toothed dolphin)"),
    ("tursiops-aduncus", "Tursiops aduncus (Indo-Pacific bottlenose dolphin)"),
    ("tursiops-truncatus", "Tursiops truncatus (Offshore bottlenose dolphin)"),
    ("tursiops-sp", "Tursiops sp. (Unidentified bottlenose dolphin)"),
    ("delphinidae-fam", "Unidentified dolphin"),
    # whales
    ("balaenoptera-acutorostrata", "Balaenoptera acutorostrata (Dwarf minke whale)"),
    ("balaenoptera-bonaerensis", "Balaenoptera bonaerensis (Antarctic minke whale)"),
    ("balaenoptera-borealis", "Balaenoptera borealis (Sei whale)"),
    ("balaenoptera-edeni", "Balaenoptera edeni (Bryde's whale)"),
    ("balaenoptera-musculus", "Balaenoptera musculus (Blue whale)"),
    ("balaenoptera-musculus-brevicauda", "Balaenoptera musculus brevicauda (Pygmy blue whale)"),
    ("balaenoptera-physalus", "Balaenoptera physalus (Fin whale)"),
    ("balaenoptera-omurai", "Balaenoptera omurai (Omura's whale)"),
    ("balaenoptera-sp", "Balaenoptera sp. (Unidentified Balaenoptera)"),
    ("caperea-marginata", "Caperea marginata (Pygmy Right Whale)"),
    ("eubalaena-australis", "Eubalaena australis (Southern right whale)"),
    ("feresa-attenuata", "Feresa attenuata (Pygmy killer whale)"),
    ("globicephala-macrorhynchus", "Globicephala macrorhynchus (Short-finned pilot whale)"),
    ("globicephala-melas", "Globicephala melas (Long-finned pilot whale)"),
    ("globicephala-sp", "Globicephala sp. (Unidentified pilot whale)"),
    ("indopacetus-pacificus", "Indopacetus pacificus (Longman's beaked whale)"),
    ("kogia-breviceps", "Kogia breviceps (Pygmy sperm whale)"),
    ("kogia-sima", "Kogia sima (Dwarf sperm whale)"),
    ("kogia-sp", "Kogia sp. (Unidentified small sperm whale)"),
    ("megaptera-novaeangliae", "Megaptera novaeangliae (Humpback whale)"),
    ("mesoplodon-bowdoini", "Mesoplodon bowdoini (Andew's beaked whale)"),
    ("mesoplodon-densirostris", "Mesoplodon densirostris (Blainville's beaked whale)"),
    ("mesoplodon-grayi", "Mesoplodon grayi (Gray's beaked whale)"),
    ("mesoplodon-hectori", "Mesoplodon hectori (Hector's beaked whale"),
    ("mesoplodon-layardii", "Mesoplodon layardii (Strap-toothed whale)"),
    ("mesoplodon-mirus", "Mesoplodon mirus (True's beaked whale)"),
    ("mesoplodon-sp", "Mesoplodon sp. (Beaked whale)"),
    ("berardius-arnuxii", "Berardius arnuxii (Giant beaked whale)"),
    ("orcinus-orca", "Orcinus orca (Killer whale)"),
    ("peponocephala-electra", "Peponocephala electra (Melon-headed whale)"),
    ("physeter-macrocephalus", "Physeter macrocephalus (Sperm whale)"),
    ("pseudorca-crassidens", "Pseudorca crassidens (False killer whale)"),
    ("ziphius-cavirostris", "Ziphius cavirostris (Cuvier's beaked whale)"),
    ("tasmacetus-shepherdi", "Tasmacetus shepherdi (Shepherd's beaked whale)"),
    ("cetacea", "Unidentified whale"),
)

PINNIPED_SPECIES_DEFAULT = "pinnipedia"
PINNIPED_SPECIES_CHOICES = (
    ("arctocephalus-forsteri", "Arctocephalus forsteri (New Zealand fur seal)"),
    ("neophoca-cinerea", "Neophoca cinerea (Australian sea lion)"),
    ("arctocephalus-tropicalis", "Arctocephalus tropicalis (Subantarctic fur seal)"),
    ("hydrurga-leptonyx", "Hydrurga leptonyx (Leopard seal)"),
    ("lobodon-carcinophagus", "Lobodon carcinophagus (Crabeater seal)"),
    ("mirounga-leonina", "Mirounga leonina (Southern elephant seal)"),
    (PINNIPED_SPECIES_DEFAULT, "Unidentified pinniped"),
)

SEASNAKE_SPECIES_DEFAULT = "hydrophiinae-subfam"
SEASNAKE_SPECIES_CHOICES = (
    (SEASNAKE_SPECIES_DEFAULT, "Hydrophiinae subfam. (Sea snakes and kraits)"),
    ("acalyptophis-sp", "Acalyptophis sp. (Horned sea snake)"),
    ("aipysurus-sp", "Aipysurus sp. (Olive sea snake)"),
    ("astrotia-sp", "Astrotia sp. (Stokes' sea snake)"),
    ("emydocephalus-sp", "Emydocephalus sp. (Turtlehead sea snake)"),
    ("enhydrina-sp", "Enhydrina sp. (Beaked sea snake)"),
    ("ephalophis-sp", "Ephalophis sp. (Grey's mudsnake)"),
    ("hydrelaps-sp", "Hydrelaps sp. (Port Darwin mudsnake)"),
    ("hydrophis-sp", "Hydrophis sp. (sea snake)"),
    ("kerilia-sp", "Kerilia sp. (Jerdon's sea snake)"),
    ("kolpophis-sp", "Kolpophis sp. (bighead sea snake)"),
    ("lapemis-sp", "Lapemis sp. (Shaw's sea snake)"),
    ("laticauda-sp", "Laticauda sp. (Sea krait)"),
    ("parahydrophis-sp", "Parahydrophis (Northern mangrove sea snake)"),
    ("parapistocalamus-sp", "Parapistocalamus sp. (Hediger's snake)"),
    ("pelamis-sp", "Pelamis sp. (Yellow-bellied sea snake)"),
    ("praescutata-sp", "Praescutata sp. (Sea snake)"),
    ("thalassophis-sp", "Thalassophis sp. (Sea snake)"),
)

SIRENIA_CHOICES = (("dugong-dugon", "Dugong dugon (Dugong)"),)

SPECIES_CHOICES = (
    NA
    + TURTLE_SPECIES_CHOICES
    + CETACEAN_SPECIES_CHOICES
    + SIRENIA_CHOICES
    + PINNIPED_SPECIES_CHOICES
    + SEASNAKE_SPECIES_CHOICES
)

UNKNOWN_VALUE = "unknown"
UNKNOWN_CHOICE = (UNKNOWN_VALUE, "Unknown")
SEX_CHOICES = (
    (NA_VALUE, "Not applicable"),
    UNKNOWN_CHOICE,
    ("male", "Male"),
    ("female", "Female"),
    ("intersex", "Hermaphrodite or intersex"),
)

TURTLE_MATURITY_CHOICES = (
    ("hatchling", "Hatchling"),
    ("post-hatchling", "Post-hatchling"),
    ("juvenile", "Juvenile"),
    ("pre-pubescent-immature", "Pre-pubescent immature"),
    ("pubescent-immature", "Pubescent immature"),
    ("sub-adult", "Sub-adult"),
    ("adult-measured", "Adult (status determined from carapace and tail measurements)"),
)

MAMMAL_MATURITY_CHOICES = (
    ("unweaned", "Unweaned immature"),
    ("weaned", "Weaned immature"),
)

MATURITY_CHOICES = (
    ((NA_VALUE, "Unknown maturity"),)
    + TURTLE_MATURITY_CHOICES
    + MAMMAL_MATURITY_CHOICES
    + (("adult", "Adult"),)
)

HEALTH_D1 = "alive-then-died"
HEALTH_D2 = "dead-edible"
HEALTH_D3 = "dead-organs-intact"
HEALTH_D4 = "dead-advanced"
HEALTH_D5 = "dead-mummified"
HEALTH_D6 = "dead-disarticulated"
DEATH_STAGES = (HEALTH_D1, HEALTH_D2, HEALTH_D3, HEALTH_D4, HEALTH_D5, HEALTH_D6)
HEALTH_CHOICES = (
    (NA_VALUE, "Unknown health"),
    ("alive", "Alive, healthy"),
    ("alive-injured", "Alive, injured"),
    (HEALTH_D1, "D1 (alive, then died)"),
    (HEALTH_D2, "D2 (dead, fresh)"),
    (HEALTH_D3, "D3 (dead, organs intact)"),
    (HEALTH_D4, "D4 (dead, organs decomposed)"),
    (HEALTH_D5, "D5 (dead, mummified)"),
    (HEALTH_D6, "D6 (dead, disarticulated)"),
    ("other", "Other"),
)

CAUSE_OF_DEATH_CHOICES = NA + (
    ("indeterminate-decomposed", "Indeterminate due to decomposition"),
    ("boat-strike", "Boat strike"),
    ("trauma-human-induced", "Human induced trauma"),
    ("trauma-animal-induced", "Animal induced trauma"),
    ("drowned-entangled-fisheries", "Drowned entangled in fisheries equipment"),
    ("drowned-entangled-infrastructure", "Drowned entangled in infrastructure"),
    ("drowned-entangled-debris", "Drowned entangled in debris"),
    ("drowned-entangled", "Drowned entangled"),
    ("drowned-other", "Drowned"),
    ("fishery-bycatch", "Fishery bycatch"),
    ("handling-accident", "Handling accident"),
    ("car-collision", "Car collision"),
    ("ingested-debris", "Ingested debris"),
    ("harvest", "Harvested for human consumption"),
    ("poisoned", "Poisoned"),
    ("misorientation", "Misorientation on beach"),
    ("natural", "Natural death"),
    ("birthing", "Birthing complications"),
    ("still-born", "Still birth"),
    ("calf-failure-to-thrive", "Calf failed to thrive"),
    ("starved", "Starvation"),
    ("stranded", "Stranding"),
    ("euthanasia-firearm", "Euthanasia by firearm"),
    ("euthanasia-injection", "Euthanasia by injection"),
    ("euthanasia-implosion", "Euthanasia by implosion"),
    ("euthanasia", "Euthanasia"),
    ("predation", "Predation"),
)

CONFIDENCE_CHOICES = NA + (
    ("guess", "Guess based on insufficient evidence"),
    ("expert-opinion", "Expert opinion based on available evidence"),
    ("validated", "Validated by authoritative source"),
)

NESTING_ACTIVITY_CHOICES = (
    ("arriving", "Arriving on beach"),
    ("approaching", "Approaching nesting site"),
    ("digging-body-pit", "Digging body pit"),
    ("excavating-egg-chamber", "Excavating egg chamber"),
    ("laying-eggs", "Laying eggs"),
    ("filling-in-egg-chamber", "Filling in egg chamber"),
    ("filling-in-nest", "Filling in nest"),
    ("camouflaging-nest", "Camouflaging nest"),
    ("returning-to-water", "Returning to water"),
    ("general-breeding-activity", "General breeding activity"),
)

STRANDING_ACTIVITY_CHOICES = (
    ("floating", "Floating (dead, sick, unable to dive, drifting in water)"),
    ("beach-washed", "Beach washed (dead, sick or stranded on beach/coast)"),
    ("beach-jumped", "Beach jumped"),
    ("carcass-tagged-released", "Carcass tagged and released"),
    ("carcass-inland", "Carcass or butchered remains found removed from coast"),
    ("captivity", "In captivity"),
    ("non-breeding", "Non-breeding activity (swimming, sleeping, feeding, etc.)"),
    ("other", "Other activity"),
)

ACTIVITY_CHOICES = NA + NESTING_ACTIVITY_CHOICES + STRANDING_ACTIVITY_CHOICES

BEACH_POSITION_CHOICES = (
    (NA_VALUE, "Unknown habitat"),
    ("beach-below-high-water", "Beach below high water mark"),
    ("beach-above-high-water", "Beach above high water mark and dune"),
    ("beach-edge-of-vegetation", "Edge of vegetation"),
    ("in-dune-vegetation", "Inside vegetation"),
)

HABITAT_CHOICES = BEACH_POSITION_CHOICES + (
    ("beach", "Beach (below vegetation line)"),
    ("bays-estuaries", "Bays, estuaries and other enclosed shallow soft sediments"),
    ("dune", "Dune"),
    ("dune-constructed-hard-substrate", "Dune, constructed hard substrate (concrete slabs, timber floors, helipad)"),
    ("dune-grass-area", "Dune, grass area"),
    ("dune-compacted-path", "Dune, hard compacted areas (road ways, paths)"),
    ("dune-rubble", "Dune, rubble, usually coral"),
    ("dune-bare-sand", "Dune, bare sand area"),
    ("dune-beneath-vegetation", "Dune, beneath tree or shrub"),
    ("slope-front-dune", "Dune, front slope"),
    ("sand-flats", "Sand flats"),
    ("slope-grass", "Slope, grass area"),
    ("slope-bare-sand", "Slope, bare sand area"),
    ("slope-beneath-vegetation", "Slope, beneath tree or shrub"),
    ("below-mean-spring-high-water-mark", "Below the mean spring high water line or current level of inundation (old db value)"),
    ("below-mshwm", "Below the mean spring high water line or current level of inundation"),
    ("lagoon-patch-reef", "Lagoon, patch reef"),
    ("lagoon-open-sand", "Lagoon, open sand areas"),
    ("mangroves", "Mangroves"),
    ("reef-coral", "Coral reef"),
    ("reef-crest-front-slope", "Reef crest (dries at low water) and front reef slope areas"),
    ("reef-flat", "Reef flat, dries at low tide"),
    ("reef-seagrass-flats", "Coral reef with seagrass flats"),
    ("reef-rocky", "Rocky reef"),
    ("open-water", "Open water"),
    ("harbour", "Harbour"),
    ("boat-ramp", "Boat ramp"),
)

HABITAT_WATER = (
    "lagoon-patch-reef",
    "lagoon-open-sand",
    "mangroves",
    "reef-coral",
    "reef-crest-front-slope",
    "reef-flat",
    "reef-seagrass-flats",
    "reef-rocky",
    "open-water",
    "harbour",
)

NESTING_SUCCESS_CHOICES = (
    (NA_VALUE, "Not applicable"),
    ("nest-with-eggs", "Nest with eggs - witnessed egg drop"),
    ("nest-unsure-of-eggs", "Nest unsure of eggs - found covered up nest mound"),
    ("unsure-if-nest", "Unsure if nest - can't tell whether nest mound present or not"),
    ("no-nest", "No nest - witnessed aborted nest or found track with no nest"),
)
NESTING_PRESENT = ("nest-with-eggs", "nest-unsure-of-eggs")

NEST_AGE_DEFAULT = "unknown"
NEST_AGE_CHOICES = (
    ("fresh", "Fresh, made last night"),
    ("missed", "Missed turtle, made within past hours"),
    ("old", "Old, made before last night"),
    (NEST_AGE_DEFAULT, "Unknown age"),
)

NEST_TYPE_DEFAULT = "track-not-assessed"
NEST_TYPE_TRACK_UNSURE = "track-unsure"
NEST_TYPE_CHOICES = (
    ("track-not-assessed", "Track, not checked for nest"),
    ("false-crawl", "Track without nest"),
    ("successful-crawl", "Track with nest"),
    (NEST_TYPE_TRACK_UNSURE, "Track, checked for nest, unsure if nest"),
    ("nest", "Nest, unhatched, no track"),  # egg counts, putting eggs back
    ("hatched-nest", "Nest, hatched"),  # hatching and emergence success
    ("body-pit", "Body pit, no track"),
)

OBSERVATION_CHOICES = (
    (NA_VALUE, "Not applicable"),
    ("absent", "Absent"),
    ("present", "Present"),
    ("yes", "Yes"),
    ("no", "No"),
)

OBSERVATION_ICONS = {
    NA_VALUE: "fa-regular fa-circle-question",
    "absent": "fa-solid fa-xmark",
    "present": "fa-solid fa-check",
    "no": "fa-solid fa-xmark",
    "yes": "fa-solid fa-check",
}

OBSERVATION_COLOURS = {
    NA_VALUE: "secondary",
    "": "secondary",
    "present": "primary",
    "absent": "dark",
    "yes": "primary",
    "no": "dark",
    False: "dark",
    True: "primary",
    "False": "dark",
    "True": "primary",
    "nest-with-eggs": "success",
    "nest-unsure-of-eggs": "success",
    "unsure-if-nest": "secondary",
    "no-nest": "dark",
}

PHOTO_CHOICES = NA + (("see photos", "See attached photos for details"),)

PHOTO_ICONS = {NA_VALUE: "fa fa-question-circle-o", "see photos": "fa fa-check"}

ACCURACY_CHOICES = (
    ("1", "To nearest 1 mm"),
    ("5", "To nearest 5 mm"),
    ("10", "To nearest 1 cm"),  # Default for stranding "measured"
    ("100", "To nearest 10 cm"),  # Default for stranding "estimated"
    ("1000", "To nearest 1 m or 1 kg"),
    ("5000", "To nearest 5 m or 5 kg"),
    ("10000", "To nearest 10 m or 10 kg"),
)

DAMAGE_TYPE_CHOICES = (
    # Amputations
    ("tip-amputated", "Tip amputation"),
    ("amputated-from-nail", "Amputation from nail"),
    ("amputated-half", "Half amputation"),
    ("amputated-entirely", "Entire amputation"),
    # Epiphytes and gross things
    ("barnacles", "Barnacles"),
    ("algal-growth", "Algal growth"),
    ("tumor", "Tumor"),
    # Tags
    ("tag-scar", "Tag scar"),
    ("tag-seen", "Tag seen but not identified"),
    # Injuries
    ("cuts", "Cuts"),
    ("boat-strike", "Boat or propeller strike"),
    ("entanglement", "Entanglement"),
    # Morphologic aberrations
    ("deformity", "Deformity"),
    # Catch-all
    ("other", "Other"),
)

DAMAGE_AGE_CHOICES = (
    ("healed-entirely", "Entirely healed"),
    ("healed-partially", "Partially healed"),
    ("fresh", "Fresh"),
    UNKNOWN_CHOICE,
)

NEST_DAMAGE_DEFAULT = "turtle"
NEST_DAMAGE_CHOICES = (
    (NEST_DAMAGE_DEFAULT, "Other turtle"),
    ("bandicoot", "Bandicoot predation"),
    ("bird", "Bird predation"),
    ("crab", "Crab predation"),
    ("croc", "Croc predation"),
    ("cyclone", "Cyclone disturbance"),
    ("dingo", "Dingo predation"),
    ("dog", "Dog predation"),
    ("cat", "Cat predation"),
    ("fox", "Fox predation"),
    ("goanna", "Goanna predation"),
    ("human", "Human"),
    ("pig", "Pig predation"),
    ("tide", "Tidal disturbance"),
    ("vehicle", "Vehicle damage"),
    UNKNOWN_CHOICE,
    ("other", "Other identifiable (see comments)"),
)

TIME_ESTIMATE_CHOICES = (
    (NA_VALUE, "Not applicable"),
    ("same-night", "Sometime that night"),
    ("plusminus-2h", "Plus/minus 2h of estimate"),
    ("plusminus-30m", "Correct to the hour"),
)

TAIL_POKE_CHOICES = (
    ("absent", "Absent"),
    ("occasional", "Occasional"),
    ("regular", "Regular"),
    ("na", "Not applicable"),
)

TURTLE_INTERACTION_CHOICES = (
    ("no-interaction", "No interaction"),
    ("net-catch-successful", "Net catch, successful"),
    ("net-catch-failed", "Net catch, failed"),
    ("rodeo-catch-successful", "Rodeo catch, successful"),
    ("rodeo-catch-failed", "Rodeo catch, failed"),
)

TISSUE_SAMPLE_TYPE_DEFAULT = "tissue"
TISSUE_SAMPLE_TYPE_CHOICES = (
    ("blood", "Blood"),
    ("biopsy", "Biopsy"),
    ("stomach-content", "Stomach content"),
    ("egg", "Egg"),
    ("skin", "Skin"),
    ("muscle", "Muscle"),
    ("liver", "Liver"),
    ("heart", "Heart"),
    ("kidney", "Kidney"),
    ("gonad", "Gonad"),
    ("fat", "Fat"),
    ("brain", "Brain"),
    ("faecal", "Faecal"),
    ("epibiota", "Epibiota"),
    ("keratin", "Keratin"),
    ("bone", "Bone"),
    (TISSUE_SAMPLE_TYPE_DEFAULT, "Other tissue"),
)
