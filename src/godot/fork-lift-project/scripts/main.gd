# scripts/main.gd
extends Node3D

@onready var forklift = $Forklift
# 보충 실습에서 추가한 바로 그 카메라입니다.
@onready var camera = $Forklift/SpringArm3D/Camera3D

# 키보드/마우스 입력이 발생할 때마다 호출됩니다.
func _input(event: InputEvent) -> void:
	# 만약 이벤트가 마우스 왼쪽 버튼을 누르는 것이라면...
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.is_pressed():
		# 현재 3D 물리 세계의 상태를 가져옵니다.
		var space_state = get_world_3d().direct_space_state
		# 카메라 위치에서 마우스 클릭 지점으로 향하는 광선(Ray)을 계산합니다.
		var from = camera.project_ray_origin(event.position)
		var to = from + camera.project_ray_normal(event.position) * 1000.0
		
		# 광선 쿼리(질의)를 생성합니다.
		var query = PhysicsRayQueryParameters3D.create(from, to)
		query.collide_with_areas = false # 감지 영역과는 충돌하지 않도록 설정
		# 광선과 충돌하는 첫 번째 물체를 찾습니다。
		var result = space_state.intersect_ray(query)
		
		# 만약 충돌한 물체가 있다면...
		if result:
			# 지게차의 set_target 함수를 호출하여 목표 지점을 설정합니다.
			if forklift.has_method("set_target"):
				forklift.set_target(result.position)
