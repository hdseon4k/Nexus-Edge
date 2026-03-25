# scripts/camera_controller.gd
extends SpringArm3D

@export var rotation_speed = 2.0
@export var zoom_speed = 0.5
@export var pan_speed = 0.01
@export var min_zoom = 2.0
@export var max_zoom = 10.0

# _unhandled_input은 마우스, 키보드 등 모든 입력을 받지만,
# UI 요소 등에서 처리된 입력은 제외하고 받습니다.
func _unhandled_input(event: InputEvent) -> void:
	# 마우스 오른쪽 버튼을 누른 상태에서 마우스를 움직이면... (회전)
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT):
		# 마우스의 수평 움직임(event.relative.x)에 따라 Y축을 중심으로 회전합니다. (좌우 회전)
		rotate_y(deg_to_rad(-event.relative.x * rotation_speed))
		# 마우스의 수직 움직임(event.relative.y)에 따라 X축을 중심으로 회전합니다. (상하 회전)
		rotate_x(deg_to_rad(event.relative.y * rotation_speed))
		# X축 회전(상하 각도)을 -70도에서 0도 사이로 제한하여 카메라가 바닥 아래를 보지 않도록 합니다.
		rotation_degrees.x = clamp(rotation_degrees.x, -70, 0)
		# 이 입력이 다른 곳에서 또 처리되지 않도록 막습니다.
		get_viewport().set_input_as_handled()

	# 마우스 휠 클릭(중간 버튼)을 누른 상태에서 마우스를 움직이면... (이동/Panning)
	if event is InputEventMouseMotion and Input.is_mouse_button_pressed(MOUSE_BUTTON_MIDDLE):
		# 카메라의 로컬 X축과 Y축 방향 벡터를 구합니다.
		var pan_vector = Vector3.ZERO
		pan_vector -= transform.basis.x * event.relative.x * pan_speed
		pan_vector += transform.basis.y * event.relative.y * pan_speed
		
		# SpringArm3D의 위치를 이동시킵니다.
		position += pan_vector
		get_viewport().set_input_as_handled()

	# 마우스 휠 스크롤 입력을 감지하면...
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP: # 휠을 위로
			spring_length = clamp(spring_length - zoom_speed, min_zoom, max_zoom)
		if event.button_index == MOUSE_BUTTON_WHEEL_DOWN: # 휠을 아래로
			spring_length = clamp(spring_length + zoom_speed, min_zoom, max_zoom)
