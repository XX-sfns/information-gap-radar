from radar.classifier import classify


def test_classifies_pricing_pain():
    item = classify("This tool is too expensive", "Pricing makes it impossible for a small team", "Reddit", "https://example.com")
    assert item.category == "价格与付费"
    assert item.audience == "团队/企业"
