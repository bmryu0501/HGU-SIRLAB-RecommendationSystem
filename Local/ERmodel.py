very_high = 70; high = 50; low = 40; very_low = 0

def get_level(engagement_score):
    if engagement_score >= very_high:
        return "VERY HIGH"
    elif engagement_score >= high:
        return "HIGH"
    elif engagement_score >= low:
        return "LOW"
    elif engagement_score >= very_low:
        return "VERY LOW"
