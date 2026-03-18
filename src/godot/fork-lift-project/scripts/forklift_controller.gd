extends VehicleBody3D

@export var max_engine_force: float = 1000.0 # 가속력
@export var max_steering: float = 0.5      # 조향각 (라디안 단위)
@export var brake_force: float = 50.0       # 제동력

func _physics_process(_delta: float) -> void:
	# 조향: 왼쪽이 +, 오른쪽이 -
	steering = Input.get_axis("ui_right", "ui_left") * max_steering
	
	# 가속: 위가 +, 아래가 -
	engine_force = Input.get_axis("ui_up", "ui_down") * max_engine_force
	
	# 제동 (Space바 등)
	if Input.is_action_pressed("ui_select"):
		brake = brake_force
	else:
		brake = 0.0



