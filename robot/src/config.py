'''
MIT License

Copyright (c) 2026 HES-SO Valais-Wallis, Engineering Track 304
'''

from pathlib import Path
import numpy as np

from URBasic.waypoint6d import TCP6D, Joint6D

PROJECT_DIR = Path(__file__).parent.parent.parent
ASSETS_DIR = PROJECT_DIR / "assets"
OUTPUT_DIR = PROJECT_DIR / "output"
DEFAULT_CALIBRATION_PATH =  PROJECT_DIR / "robot" / "duckify_simulation" / "defaults" / "calibration_default.pkl"
TEST_PEN_CALIBRATION_PATH = PROJECT_DIR / "robot" / "duckify_simulation" / "defaults" / "pen_calibration_test.pkl"
TEST_TRANSFORMATION_PATH =  PROJECT_DIR / "robot" / "duckify_simulation" / "defaults" / "transformation_test.pkl"
DEFAULT_FORCE_PATH = OUTPUT_DIR / "force_log.csv"
DEFAULT_DATA_DIR = OUTPUT_DIR / "data"

# DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv-test_1_triangle-trace.json"
# DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv-test_1_triangle-trace.json"
# DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv_v2-test_14_full_body_line-trace.json"
# DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv_v2-test_11_long_line-trace.json"
# DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv-test_4_triangle_on_bill-trace.json"
DEFAULT_JSON_OBJECT = ASSETS_DIR / "tests" / "duck_uv_v2-test_15_colored_lines-trace.json"



DEFAULT_JSON_SOCLE = PROJECT_DIR / "robot" / "duckify_simulation" / "defaults" / "calibration_transformation.json"

URDF_PATH = Path(__file__).resolve().parents[1] / 'duckify_simulation' / 'urdf' / 'ur3e.urdf'

# Link indices for the flattened UR3e URDF:
#   1=base_link_inertia, 2=shoulder, 3=upper_arm, 4=forearm,
#   5=wrist_1, 6=wrist_2, 7=wrist_3, 8=flange, 9=tool0,
#   10=wrist_cam, 11=hande_base, 12=left_finger, 13=right_finger, 14=pen
SELF_COLLISION_PAIRS = [
    (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9),
    (1, 10), (1, 11), (1, 12), (1, 13), (1, 14),
    (2, 5), (2, 6), (2, 7), (2, 8), (2, 9),
    (2, 10), (2, 11), (2, 12), (2, 13), (2, 14),
    (3, 6), (3, 7), (3, 8), (3, 9),
    (3, 10), (3, 11), (3, 12), (3, 13), (3, 14),
    (4, 7), (4, 8), (4, 9),
    (4, 10), (4, 11), (4, 12), (4, 13), (4, 14),
]

VERBOSE = True
FORCE_ENABLE = False

# Create a new ISCoin object
# UR3e1 IP (closest to window): 10.30.5.158
# UR3e2 IP: 10.30.5.159
ROBOT_IP = "10.30.5.159"

# Collision margins
COLLISION_MARGIN = 0            # margin for obstacle collision checks
SELF_COLLISION_MARGIN = 0.012  # margin for self-collision checks
MAX_JOINT_JUMP = 1         # max allowed single-joint difference from qnear in radians
MAX_JOINT_RANGE = 4.5      # max allowed absolute joint angle in radians
MIN_HEIGHT_NORMAL_CORRECTION_MM = 25
MIN_HEIGHT_ACCEPTANCE = 10

# Default home position
HOMEJ = Joint6D.createFromRadians(1.8859, -1.4452, 1.2389, -1.3639, -1.5693, -0.3849)
FIXED_THETA6 = None
FIRST_SIMULATION_PEN_SUPPORT = TCP6D.createFromMetersRadians(-0.31030073427776544, -0.12772318658605364, 0.1691221791937419, -3.123526746656135, 0.06494033931935389, 0.0007571664234476744)
SECOND_SIMULATION_PENSUPPORT = TCP6D.createFromMetersRadians(-0.37030073427776544, -0.12772318658605364, 0.1691221791937419, -3.123526746656135, 0.06494033931935389, 0.0007571664234476744)


# MINIMAL_DISTANCE = 0.164
OFFSET_Z = 1.4
MINIMAL_DISTANCE = 0.018

LEGNTH_BETWEEN_PENS = 0.05 # This distance comes from the design of the wood support for pen.
FACING_DOWN = (np.pi, 0, 0) # To maintain the gripper facing down
SECURITY_APPROACH = 0.075

GRIPPER_LENGTH = 0.101
PEN_LENGTH = 0.128
# PEN_POS_0 =  [-0.3, -0.172, MINIMAL_DISTANCE] # Position of pen at index 0


# Free-space travel constraints
TCP_Y_MAX        = 0.0      # TCP must stay at Y ≤ 0
TCP_Z_MIN        = 0.0      # TCP must stay at Z ≥ 0
TCP_Z_MAX        = 0.5      # TCP must stay at Z ≤ 0.5
LINK_Z_MIN       = {
    2: 0.10,                 # elbow must stay above 10 cm
    3: 0.10,                 # upper_arm_link must stay above 10 cm
    4: 0.10,                 # forearm_link must stay above 10 cm
}
UR3E_MAX_REACH   = None      # disabled — IK solver handles reachability
FREE_TRAVEL_STEP = 0.005    # meters — interpolation density for path validation

JOINT_LIMITS = [
    None,              # shoulder_pan
    None,              # shoulder_lift
    None,              # elbow
    None,              # wrist_1
    None,              # wrist_2
    None,              # wrist_3
]

# Motion parameters
DRAW_V = 0.1
DRAW_A = 0.5
APPROACH_V = 0.1
APPROACH_A = 0.5
TRAVEL_V = 0.25
TRAVEL_A = 1.2
HOVER_OFFSET = [0, 0, -0.01, 0, 0, 0]

TCP_REF_VAL = [1.30905845e-04, 3.33683034e-04, 2.45280738e-01]
# Calibration points, used as default
TCPS_20 = [
    [0.09923226380963619, -0.3936237333456494, 0.2241707102377116, 0.576534502783353, -2.801623474567781, -0.4841337776020336],
    [-0.05415645689244093, -0.3953984087553033, 0.21928851997659993, 0.23402931706237418, 2.778033572687844, 0.45840199634357587],
    [-0.054524138620445695, -0.39546163267180845, 0.2194560899784096, 0.2335390262119786, 2.783785824873644, 0.4510348107203675],
    [0.0752223292033933, -0.40520983496228175, 0.2260599738507684, 0.4572457692623414, -2.9109062545914886, -0.5364679269112991],
    [0.0829983763105315, -0.3145440306229818, 0.23651078628355368, 0.3951666302237936, -2.8778640875293946, 0.020826760853426392],
    [0.17537792453011916, -0.27966304416915055, 0.1871802429879547, 0.4399208472865239, -2.4166507384311493, 0.11158336986030104],
    [-0.11994350407194002, -0.2833976738613014, 0.18952203929656486, -0.11587882239515394, 2.488783491737581, -0.2874871978684851],
    [0.042587583213620814, -0.42502159418902, 0.2219296443030877, -1.819892078036102, 2.2285954928177354, 0.5297978049692356],
    [0.04244370933942005, -0.42547028481239557, 0.22238439939526014, -1.8232450157901965, 2.2322450410810823, 0.5277815763416596],
    [0.020874413390515264, -0.34192399335641094, 0.2416659479631329, -1.6019421625827266, 2.6368378551232445, 0.06821140243218453],
    [0.020803283214023204, -0.3418580959196876, 0.24363220771625155, -1.6034030755162376, 2.6412352323485133, 0.06264503078869965],
    [-0.0790726920318296, -0.26904313811943686, 0.21128926726360914, -1.5548308665720385, 2.3598614347530305, -0.6531326432466081],
    [0.0427270175708247, -0.2473905824164213, 0.2299557666201055, 2.1997240823524864, -1.7930464879794845, 0.21897511307224746],
    [0.13236126549367827, -0.37709210594126424, 0.2134888319694367, 2.113428037038218, -2.0042534442643, -0.709899151721018],
    [0.053381366331223756, -0.3159752956877128, 0.24229245067174737, 1.8209996559857016, -2.4222938552259685, -0.050512659771693856],
    [-0.049955483412195634, -0.41217334754184276, 0.21506155931685994, -1.6191731898646298, 2.109641966964828, 0.12393449118187727],
    [0.11965373370731985, -0.426189467377058, 0.20111114739956754, -2.3836120944741555, 1.6242241381287574, 0.8568802013152502],
    [0.1072294696915219, -0.2674062588065899, 0.22084409245177472, 2.144447557404073, -1.698541221842688, -0.16060169509460684],
    [-0.10731169114667957, -0.19413670798855612, 0.15654354818487162, 2.3277646358217945, -1.2822755883172325, 1.191980512607587],
    [0.020926595559954138, -0.3139355562333332, 0.24095599082082952, 3.0691506381776072, -0.3992164073191759, 0.04457895483726155],
]

# Default object-to-robot transform parameters
OBJ2ROBOT_RZ_DEG       = 0.0
OBJ2ROBOT_TRANSLATION  = (0.32, -0.4, 0.155)
OBJ2ROBOT_SCALE        = 0.001          # mm → meters

OFFSET_Z_HOTFIX = 0.0 # temporary hotfix for the double tape

TEST_TRANSFORMATION = [0, 0, 2, 0, 0, -1]  # x, y, z, n1, n2, n3

# Scene for pybullet collision testing
OBSTACLE_STLS = [
    {
        # 'path': ASSETS_DIR / 'models/duck_uv.stl',
        'path': ASSETS_DIR / 'models/duck_uv_low_poly.stl',
        'scale': [0.001, 0.001, 0.001],
    },
    {
        'path': ASSETS_DIR / 'models/workspace.stl',
        'scale': [1, 1, 1],
        'position': [0, 0, 0],
        'orientation': [0, 0, 0, 1],
        'exclude_links': [1, 2, 3, 4],
    },
    {
        'path': ASSETS_DIR / 'models/support_duck_simulation.stl',
        'scale': [0.001, 0.001, 0.001],
    },
]

DRAWING_ANGLE = 25

CONE_TILT_STEP = 2.5
CONE_AZIMUTH_STEP = 2.5

CONE_SEARCH_MODE = 2  # 0 = fast, 1 = ring by ring, 2 = all