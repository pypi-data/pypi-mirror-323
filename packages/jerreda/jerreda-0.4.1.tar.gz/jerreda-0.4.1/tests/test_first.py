import pandas as pd
from jerreda.cli import group_by_count, add_keyword_count
import pytest

def test_all_count_keyword_sum():
    df = add_keyword_count(keyword="자유", keyword_sum=True)
    
    assert isinstance(df, pd.DataFrame)
    assert "keyword_sum" in df.columns

    # count 보다 keyword_sum이 크거나 같은 경우
    assert (df["count"] <= df["keyword_sum"]).all()

@pytest.mark.skip()
def test_dictionary():
    df = group_by_count("자유")
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 12

    for p_name, s_count in president_speeches.items():
        president_row = df[df['president'] == p_name]
        assert president_row.iloc[0]['count'] == s_count

def test_search_exception():
    row_cnt = 13
    df = group_by_count(keyword="자유", asc=True, rcnt=row_cnt)

    # assert
    assert isinstance(df, pd.DataFrame)
    assert len(df) < row_cnt

def test_sort_with_limited_row():
    row_cnt = 3
    is_asc = True

    df = group_by_count(keyword="자유", asc=is_asc, rcnt=row_cnt)

    assert isinstance(df, pd.DataFrame)
    assert df.iloc[0]["president"] == "윤보선"
    assert len(df) == row_cnt

def test_group_count_by_free():
    input_data = group_by_count(keyword="자유", asc=False, rcnt=12)
    
    # 결과값이 존재하는지 검증
    assert input_data is not None

    # '자유' 키워드를 입력했을 때의 예상 결과
    data = {
         "president": ["박정희", "이승만", "노태우", "김대중", "문재인", 
                       "김영삼", "이명박", "전두환", "노무현", "박근혜", 
                       "최규하", "윤보선"],
         "count": [513, 438, 399, 305, 275, 
                   274, 262, 242, 230, 111, 
                   14, 1]
    }
    expected_data = pd.DataFrame(data)
    
    # 예상 결과와 일치하는지 검증
    assert input_data.equals(expected_data), "\n'자유' 키워드는 예상 데이터와 일치하지 않습니다."

def test_group_count_by_demo():
    input_data = group_by_count(keyword="민주주의", asc=False, rcnt=12)

    # 결과값이 존재하는지 검증
    assert input_data is not None

    # '민주주의' 키워드를 입력했을 때의 예상 결과
    data = {
         "president": ["노태우", "김대중", "문재인", "노무현", "김영삼",
                       "이명박", "박정희", "전두환", "이승만", "박근혜",
                       "최규하", "윤보선"],
         "count": [402, 329, 237, 230, 203,
                   174, 163, 137, 116, 52,
                   7, 1]
    }
    expected_data = pd.DataFrame(data)

    # 예상 결과와 일치하는지 검증
    assert input_data.equals(expected_data), "\n'민주주의' 키워드는 예상 데이터와 일치하지 않습니다."

def test_group_count_by_jerry():
    input_data = group_by_count(keyword="권오준", asc=False, rcnt=5)

    # 결과값이 존재하는지 검증
    # '권오준' 키워드가 들어간 데이터가 존재하지 않아야 함
    assert input_data is None
