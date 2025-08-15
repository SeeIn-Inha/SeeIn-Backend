import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000"

def test_user_management():
    """사용자 관리 기능 테스트"""
    
    # 1. 회원가입
    print("=== 1. 회원가입 테스트 ===")
    register_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "username": "테스트유저"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"회원가입 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"회원가입 성공: {response.json()}")
    else:
        print(f"회원가입 실패: {response.text}")
        return
    
    # 2. 로그인
    print("\n=== 2. 로그인 테스트 ===")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"로그인 응답: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"로그인 성공: {token_data}")
    else:
        print(f"로그인 실패: {response.text}")
        return
    
    # 헤더 설정
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 3. 현재 사용자 정보 조회
    print("\n=== 3. 현재 사용자 정보 조회 ===")
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"사용자 정보 조회 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"사용자 정보: {response.json()}")
    else:
        print(f"사용자 정보 조회 실패: {response.text}")
    
    # 4. 사용자 정보 수정 (닉네임 변경)
    print("\n=== 4. 닉네임 변경 테스트 ===")
    update_data = {
        "username": "새로운닉네임"
    }
    
    response = requests.put(f"{BASE_URL}/auth/update", json=update_data, headers=headers)
    print(f"닉네임 변경 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"닉네임 변경 성공: {response.json()}")
    else:
        print(f"닉네임 변경 실패: {response.text}")
    
    # 5. 사용자 정보 수정 (이메일 변경)
    print("\n=== 5. 이메일 변경 테스트 ===")
    update_data = {
        "email": "newemail@example.com"
    }
    
    response = requests.put(f"{BASE_URL}/auth/update", json=update_data, headers=headers)
    print(f"이메일 변경 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"이메일 변경 성공: {response.json()}")
        # 토큰 갱신을 위해 다시 로그인
        login_data["email"] = "newemail@example.com"
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            print("토큰 갱신 완료")
    else:
        print(f"이메일 변경 실패: {response.text}")
    
    # 6. 비밀번호 변경
    print("\n=== 6. 비밀번호 변경 테스트 ===")
    password_update_data = {
        "current_password": "testpassword123",
        "new_password": "newpassword123"
    }
    
    response = requests.put(f"{BASE_URL}/auth/change-password", json=password_update_data, headers=headers)
    print(f"비밀번호 변경 응답: {response.status_code}")
    if response.status_code == 200:
        print(f"비밀번호 변경 성공: {response.json()}")
    else:
        print(f"비밀번호 변경 실패: {response.text}")
    
    # 7. 회원 탈퇴 (실제로는 주석 처리하여 테스트)
    print("\n=== 7. 회원 탈퇴 테스트 (실행하지 않음) ===")
    print("회원 탈퇴는 실제로 실행하지 않고 예시만 보여줍니다.")
    
    delete_data = {
        "password": "newpassword123"
    }
    
    # 실제 실행하려면 아래 주석을 해제하세요
    # response = requests.delete(f"{BASE_URL}/auth/delete", json=delete_data, headers=headers)
    # print(f"회원 탈퇴 응답: {response.status_code}")
    # if response.status_code == 200:
    #     print(f"회원 탈퇴 성공: {response.json()}")
    # else:
    #     print(f"회원 탈퇴 실패: {response.text}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    test_user_management()
