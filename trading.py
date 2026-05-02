def calculate_volume(highest, lowest):
    """최고가와 최저가의 차이의 절반인 volume을 계산합니다."""
    return (highest - lowest) * 0.5

def go_long(highest, lowest, next_start):
    """매수(long) 진입가와 손절가를 계산하여 출력합니다."""
    volume = calculate_volume(highest, lowest)
    go_in = next_start + volume
    cut_off = lowest
    print(f"매수 진입가: {go_in:.4f}, 손절가: {cut_off:.4f}")

def go_short(highest, lowest, next_start):
    """매도(short) 진입가와 손절가를 계산하여 출력합니다."""
    volume = calculate_volume(highest, lowest)
    go_in = next_start - volume
    cut_off = highest
    print(f"매도 진입가: {go_in:.4f}, 손절가: {cut_off:.4f}")

# --- 사용자 입력 처리 ---

short_or_long = input("short 또는 long을 입력하세요: ").lower() # 소문자로 변환

try:
    # 3가지 소수(float) 값을 입력받고 할당
    highest, lowest, next_start = map(float, input("최고가, 최저가, 다음 시작가를 공백으로 구분하여 입력하세요: ").split())
except ValueError:
    print("❌ 잘못된 입력입니다. 세 가지 숫자를 공백으로 구분하여 정확히 입력해주세요.")
    # 프로그램 종료
    exit()

# --- 로직 실행 ---

if short_or_long == "short":
    go_short(highest, lowest, next_start)
elif short_or_long == "long":
    go_long(highest, lowest, next_start)
else:
    print("❌ 'short' 또는 'long'만 입력 가능합니다. 다시 시작해주세요.")