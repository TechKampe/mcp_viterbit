"""
Configuration and constants for the Viterbit MCP server.
"""
import os
from typing import Dict

# --- Viterbit API Configuration ---
VITERBIT_API_KEY = os.getenv("VITERBIT_API_KEY")
BASE_URL = "https://api.viterbit.com/v1"

# --- Viterbit Stage Constants ---
STAGE_MATCH = "Match"
STAGE_CONTRATADO = "Contratado"

# --- Custom Field Question IDs ---
# These can be overridden via environment variables for different Viterbit instances
DISCORD_ID_QUESTION_ID = os.getenv("DISCORD_ID_QUESTION_ID", "67f69c61c26ebcaa2f024ea3")
SUSCRIPTOR_QUESTION_ID = os.getenv("SUSCRIPTOR_QUESTION_ID", "67fe75c8f8e7996e110cb5a0")
CUSTOM_FIELD_STAGE_NAME_ID = os.getenv("CUSTOM_FIELD_STAGE_NAME_ID", "682c9947fdbad58c810ddb8a")
CUSTOM_FIELD_STAGE_DATE_ID = os.getenv("CUSTOM_FIELD_STAGE_DATE_ID", "6821ff159432bfca8407fbe4")
CUSTOM_FIELD_SIN_DISCORD_ID = os.getenv("CUSTOM_FIELD_SIN_DISCORD_ID", "67f7669d8ca233a54a0a4cea")
CUSTOM_FIELD_NOMBRE_EMPRESA_ID = os.getenv("CUSTOM_FIELD_NOMBRE_EMPRESA_ID", "680a5be6ed5349b09707b6ed")

# Additional Custom Field IDs for subscriber filtering
GARANTIA_100_DIAS_ID = os.getenv("GARANTIA_100_DIAS_ID", "68bea397f801385f0f0e0088")
ACTIVO_INACTIVO_ID = os.getenv("ACTIVO_INACTIVO_ID", "68a455d5585b0d17c20bdcb1")

# Location/Zone Custom Field IDs
ZONA_FIELD_ID = "67c83def159fcdd58906e4c5"  # Zona
PROVINCIA_FIELD_ID = "67c84b1c21bda2b3c60fabea"  # Provincia

# Additional field IDs for reference (from custom fields API):
# "Carnet de Conducir": "6748889b1207a9f3040c4a8a"
# "Nivel de educación": "6748889b1207a9f3040c4a8b"
# "Movilidad Nacional": "67c8200c62e3ae6c1006691b"
# "Movilidad Internacional": "67c8200c62e3ae6c1006691a"
# "Experiencia relacionada": "67c8412097b7cbb331024e09"
# "Coach": "68c14707fdded0284e03159c"
# "Oficio preferente": "68a455d5585b0d17c20bdcb3"

# --- Department Lookup ---
DEPARTMENT_LOOKUP: Dict[str, str] = {
    "Aerotermia": "6823708a92b2ec408603a9aa",
    "Electricidad": "674882703e806a32920f1c07",
    "Fontanería": "682370bd680b48a79a0d5e73",
    "Instalaciones": "682370c9b53725e32a021be9",
    "Mantenimiento general": "682370d5095d26419f0749f9",
    "Mecánica": "682370e104990151bc037c18",
    "Climatización": "6823645b14b4f3d6cf0437e2",
    "Gas": "682370c39aa0d1ef33070e81",
    "Albañilería": "682364697248dfd911005c94",
    "Soldadura": "682370edd758cbaa060c2257",
    "Telecomunicaciones": "682370f383b0e1c2af0a8a2f",
    "Maquinista": "682370dae0c16a69fd0457b4",
    "Pintura": "682370e72d85ff622c023353",
    "Energías Renovables": "67488288a1ae68e8920419cd",
    "Cristalería": "682da6d711ae26612408119c",
    "Aluminería": "682da6ced2805005700b889d",
    "Producción": "682da6c54cc9378d560ba721",
    "Oficios": "67f78168e15674453b0c34b1"
}

# --- Location Lookup ---
LOCATION_LOOKUP: Dict[str, str] = {
    "Madrid": "674f2f46c51a95550a07e205",
    "Valencia": "6750104751972bd5c4034f61",
    "Ourense": "67500f5d09cac50dbe062127",
    "Tarragona": "675011443cc983b9e90b0c85",
    "Lleida": "682444c64d6590aac40cf58d",
    "Málaga": "675010dfbea835b2440414ba",
    "Bilbao": "6750120b319ca9668909f319",
    "Cadiz": "6750107dc737fb3bca0ca3c2",
    "Castellón": "67501110c30a8e4c1c01becc",
    "Salamanca": "68244593c5f75e96640ed0e6",
    "Barcelona": "6750123a1496b55c61068d3d",
    "Segovia": "675010a8c30a8e4c1c01bec0",
    "Jaén": "6824446f8925c0253803b671",
    "Toledo": "6824463e74e85ce43b060d33",
    "Murcia": "67502cf3c9f7fbd36d083027",
    "Palma de Mallorca": "6824445dafc1fcfb300110f4",
    "Navarra": "68244530f1097783be0424bc",
    "León": "682444b3c2490915090b06e8",
    "Sevilla": "682445dcb0b47d4993085917",
    "Zaragoza": "675011b1521ee3d3cb05b5a2",
    "Alicante": "6824425a8a9153c125067c92",
    "Ciudad Real": "6824439b17474c2ca50b1311"
}

# --- Default disqualified_by_id for candidature disqualification ---
DEFAULT_DISQUALIFIED_BY_ID = "67496bc419367fe3810c6412"