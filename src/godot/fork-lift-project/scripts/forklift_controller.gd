extends VehicleBody3D

# --- 기존 변수들 ---
@export var max_engine_force: float = 1000.0
@export var max_steering: float = 0.5
@export var brake_force: float = 50.0

# --- 3일차 추가 변수 ---
# @onready: 노드가 Scene에 추가되고 준비가 완료되면 변수를 초기화합니다.
# $NavigationAgent3D: Scene 트리에서 자식 노드인 NavigationAgent3D를 찾아 할당합니다.
@onready var navigation_agent: NavigationAgent3D = $NavigationAgent3D
var target_position: Vector3 = Vector3.ZERO # 최종 목표 지점을 저장할 변수

# --- 4일차 추가 변수 ---
@onready var fork: AnimatableBody3D = $Fork
@onready var sensors: Node3D = $Sensors
@onready var headlights: Node3D = $Headlights
@onready var tail_lights: Node3D = $TailLights
@export var lift_speed: float = 1.0
@export var max_lift_height: float = 2.0
@export var min_lift_height: float = 0.0

# --- 시그널 (5일차 HUD 연동 준비) ---
signal target_updated(target_pos: Vector3)


# --- 자율/수동 주행 상태 변수 ---
var is_navigating: bool = false # 자율 주행 모드 여부를 나타내는 플래그
var autonomous_gear: int = 1 # 자율 주행 기어 (1: 전진, -1: 후진)


# 외부에서 호출하여 목표 지점을 설정하는 함수
func set_target(target_pos: Vector3):
	target_position = target_pos
	# NavigationAgent에게 최종 목표 지점을 알려줍니다.
	navigation_agent.target_position = target_pos
	emit_signal("target_updated", target_pos)
	# 목표가 설정되면 자율 주행 모드를 활성화합니다.
	is_navigating = true
	# 초기 기어는 전진으로 설정
	autonomous_gear = 1
	# 내비게이션 에이전트의 경로 업데이트 강제
	navigation_agent.target_position = target_pos

func _ready() -> void:
	# 센서들이 지게차 본체와 포크를 무시하도록 설정
	if sensors:
		for ray in sensors.get_children():
			if ray is RayCast3D:
				ray.add_exception(self)
				if fork:
					ray.add_exception(fork)

# 장애물 감지 확인 함수
func check_for_obstacles() -> bool:
	if not sensors: return false
	
	for ray in sensors.get_children():
		if ray is RayCast3D and ray.is_colliding():
			return true
	return false

# 물리 프레임마다 호출되는 함수
func _physics_process(delta: float) -> void:
	# 1. 장애물 감지 및 AEB (비상 제동)
	var obstacle_detected = check_for_obstacles()

	# 2. 리프트 조작 로직 (PageUp/PageDown 키)
	var lift_direction = Input.get_axis("ui_page_down", "ui_page_up")
	if fork:
		var new_y = fork.position.y + (lift_direction * lift_speed * delta)
		new_y = clamp(new_y, min_lift_height, max_lift_height)
		fork.position.y = new_y
		# 5일차 추가: 3D 레이블 업데이트 (단계 3)
		if height_label:
			height_label.text = "Height: %.2fm" % fork.position.y

	# 3. 주행 로직
	# 수동 조작 입력을 먼저 확인합니다.
	var steer_input = Input.get_axis("ui_left", "ui_right")
	var engine_input = Input.get_axis("ui_up", "ui_down")

	# 방향키 입력이 감지되면, 수동 모드로 전환합니다.
	if steer_input != 0 or engine_input != 0:
		is_navigating = false

	if obstacle_detected:
		# 장애물이 있으면 무조건 엔진 정지 및 브레이크 최대 작동
		engine_force = 0.0
		brake = brake_force
	elif is_navigating:
		# --- 자율 주행 모드 ---
		if navigation_agent.is_navigation_finished():
			# 목표에 도달하면 자율 주행을 멈추고 브레이크를 겁니다.
			is_navigating = false
			engine_force = 0.0
			steering = 0.0
			brake = brake_force
		else:
			brake = 0.0 # 주행 중이므로 브레이크 해제
			
			# 다음 경로 지점 계산
			var next_path_pos = navigation_agent.get_next_path_position()
			var direction_to_next_vec = (next_path_pos - global_position).normalized()
			
			# 전방 및 후방 벡터
			var forward_vector = -global_transform.basis.z
			var backward_vector = global_transform.basis.z
			
			# 전방과의 각도 차이 계산
			var forward_angle = forward_vector.signed_angle_to(direction_to_next_vec, Vector3.UP)
			
			# --- 기어 로직 (Gear Logic) ---
			# 목적지가 정면 기준 약 110도 이상 뒤에 있으면 후진 기어 선택
			if abs(forward_angle) > 1.9: # 약 110도
				autonomous_gear = -1
			# 목적지가 정면 기준 약 60도 이내로 들어오면 전진 기어 선택
			elif abs(forward_angle) < 1.0: # 약 60도
				autonomous_gear = 1
			
			# --- 조향 및 엔진 힘 적용 ---
			if autonomous_gear == 1:
				# 전진: 정면 벡터 기준으로 조향
				steering = clamp(-forward_angle, -max_steering, max_steering)
				# 감속 로직 적용하여 엔진 힘 설정 (음수는 전진)
				var distance_to_target = global_position.distance_to(target_position)
				var speed_scale = clamp(inverse_lerp(navigation_agent.target_desired_distance, 5.0, distance_to_target), 0.1, 1.0)
				engine_force = -(max_engine_force * 0.5) * speed_scale
			else:
				# 후진: 후방 벡터 기준으로 조향 (후륜 조향 특성 반영)
				var backward_angle = backward_vector.signed_angle_to(direction_to_next_vec, Vector3.UP)
				steering = clamp(backward_angle, -max_steering, max_steering)
				# 후진 시에는 약간 더 천천히 이동 (양수는 후진)
				engine_force = (max_engine_force * 0.3)
	else:
		# --- 수동 조작 모드 ---
		engine_force = engine_input * max_engine_force
		steering = steer_input * max_steering
		
		# 입력이 없을 때는 브레이크를 걸어 밀림을 방지합니다. (Parking Brake)
		if engine_input == 0:
			brake = brake_force * 0.5 # 50%의 힘으로 브레이크 유지
		else:
			brake = 0.0

	# 스페이스바를 누르면 강제로 브레이크가 작동하도록 합니다. (우선순위 높음)
	if Input.is_action_pressed("ui_select"):
		brake = brake_force
