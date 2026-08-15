# ============================================================
# 注文管理システム（リファクタリング演習用）
# ============================================================
# このコードには複数の問題点があります。
# 以下の観点で問題点をすべてリストアップし、改善案を作成してください。
#
# チェック観点:
#   1. DRY原則 — 重複しているロジックはどこか？
#   2. SRP    — 1つの関数が複数の責務を持っていないか？
#   3. 命名   — 変数名・関数名は意図を正確に伝えているか？
#   4. マジックナンバー — 意味不明な数値が直書きされていないか？
#   5. エラー処理 — 存在しないIDが渡された場合どうなるか？
#   6. 変更容易性 — 新しい割引コードや送料ルールを追加するとき、
#                   何箇所を修正する必要があるか？
# ============================================================


def process_order(cid, items, dc):
    n = ""
    e = ""
    if cid == 1:
        n = "田中太郎"
        e = "tanaka@example.com"
    elif cid == 2:
        n = "鈴木花子"
        e = "suzuki@example.com"
    elif cid == 3:
        n = "佐藤次郎"
        e = "sato@example.com"

    t = 0
    for item in items:
        if item["type"] == "food":
            t = t + item["p"] * item["q"]
        elif item["type"] == "electronics":
            t = t + item["p"] * item["q"]
        elif item["type"] == "clothing":
            t = t + item["p"] * item["q"]
        elif item["type"] == "books":
            t = t + item["p"] * item["q"]

    if dc == "GOLD10":
        t = t * 0.9
    elif dc == "SILVER5":
        t = t * 0.95
    elif dc == "SUMMER20":
        t = t * 0.8
    elif dc == "WINTER15":
        t = t * 0.85

    s = 0
    if t < 3000:
        s = 500
    elif t >= 3000 and t < 5000:
        s = 300
    elif t >= 5000:
        s = 0

    ft = t + s

    print("メール送信先: " + e)
    print("件名: ご注文確認 - 合計金額: " + str(ft) + "円")
    print(
        "本文: "
        + n
        + "様、ご注文ありがとうございます。合計金額は"
        + str(ft)
        + "円です。"
    )

    for item in items:
        if item["type"] == "food":
            print(
                "食品 " + item["name"] + " の在庫を" + str(item["q"]) + "個減らします"
            )
        elif item["type"] == "electronics":
            print(
                "電子機器 "
                + item["name"]
                + " の在庫を"
                + str(item["q"])
                + "個減らします"
            )
        elif item["type"] == "clothing":
            print(
                "衣料品 " + item["name"] + " の在庫を" + str(item["q"]) + "個減らします"
            )
        elif item["type"] == "books":
            print(
                "書籍 " + item["name"] + " の在庫を" + str(item["q"]) + "個減らします"
            )

    return {
        "customer_id": cid,
        "items": items,
        "subtotal": t,
        "shipping": s,
        "total": ft,
        "status": "pending",
    }


def process_return(cid, items, reason):
    n = ""
    e = ""
    if cid == 1:
        n = "田中太郎"
        e = "tanaka@example.com"
    elif cid == 2:
        n = "鈴木花子"
        e = "suzuki@example.com"
    elif cid == 3:
        n = "佐藤次郎"
        e = "sato@example.com"

    r = 0
    for item in items:
        if item["type"] == "food":
            r = r + item["p"] * item["q"]
        elif item["type"] == "electronics":
            r = r + item["p"] * item["q"]
        elif item["type"] == "clothing":
            r = r + item["p"] * item["q"]
        elif item["type"] == "books":
            r = r + item["p"] * item["q"]

    print("メール送信先: " + e)
    print("件名: 返金処理完了 - 返金金額: " + str(r) + "円")
    print("本文: " + n + "様、返品を受け付けました。返金金額は" + str(r) + "円です。")

    return {
        "customer_id": cid,
        "refund_amount": r,
        "reason": reason,
        "status": "refunded",
    }


def check_order_status(cid, order_id):
    n = ""
    e = ""
    if cid == 1:
        n = "田中太郎"
        e = "tanaka@example.com"
    elif cid == 2:
        n = "鈴木花子"
        e = "suzuki@example.com"
    elif cid == 3:
        n = "佐藤次郎"
        e = "sato@example.com"

    status = "shipped"

    print("メール送信先: " + e)
    print("件名: 注文状況のお知らせ")
    print(
        "本文: "
        + n
        + "様、ご注文(ID:"
        + str(order_id)
        + ")の現在のステータス: "
        + status
    )

    return {"order_id": order_id, "customer_id": cid, "status": status}


# ============================================================
# 動作確認用サンプルデータ
# ============================================================
if __name__ == "__main__":
    sample_items = [
        {"name": "りんご", "type": "food", "p": 200, "q": 3},
        {"name": "スマホケース", "type": "electronics", "p": 1500, "q": 1},
        {"name": "Tシャツ", "type": "clothing", "p": 2000, "q": 2},
    ]

    print("=== 注文処理 ===")
    order = process_order(1, sample_items, "GOLD10")
    print(order)

    print("\n=== 返品処理 ===")
    ret = process_return(2, sample_items[:1], "破損")
    print(ret)

    print("\n=== 注文状況確認 ===")
    status = check_order_status(1, 12345)
    print(status)
