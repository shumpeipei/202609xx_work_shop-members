# ============================================================
# 注文管理システム（リファクタリング後 — 模範解答）
# ============================================================
# 【全体共有セッション終了後に配布してください】
#
# 改善ポイント一覧:
#   1. 顧客データを CUSTOMERS 定数に集約 → DRY原則（同じ定義が3箇所にあった）
#   2. 割引率を DISCOUNT_RATES 辞書に → if/elif 爆発を解消、OCP準拠
#   3. 送料ルールを SHIPPING_RULES テーブルに → マジックナンバーを排除
#   4. get_customer() を共通関数として抽出 → DRY原則
#   5. calculate_subtotal() を分離 → SRP、テスト可能な単位に
#   6. calculate_discount() を分離 → SRP
#   7. calculate_shipping() を分離 → SRP
#   8. send_email() を分離 → DRY原則（メール送信が3箇所にあった）
#   9. update_inventory() を分離 → SRP
#  10. 変数名を意図が伝わる名前に変更 (c→customer, t→subtotal, s→shipping 等)
#  11. f-string を使用（文字列連結を廃止）
#  12. 型ヒントを追加（IDEによる静的解析を支援）
#  13. ガード節パターン（存在しない顧客IDへのエラー処理）
# ============================================================

from typing import Optional

# 顧客マスタ（実際はDBから取得する想定）
CUSTOMERS: dict[int, dict] = {
    1: {"name": "田中太郎", "email": "tanaka@example.com", "rank": "gold"},
    2: {"name": "鈴木花子", "email": "suzuki@example.com", "rank": "silver"},
    3: {"name": "佐藤次郎", "email": "sato@example.com", "rank": "bronze"},
}

# 割引コード → 割引率のマッピング（新コード追加はここだけ変えればよい）
DISCOUNT_RATES: dict[str, float] = {
    "GOLD10": 0.10,
    "SILVER5": 0.05,
    "SUMMER20": 0.20,
    "WINTER15": 0.15,
}

# 送料ルール: (小計の下限金額, 送料) を降順で定義
# 新ルール追加・変更はここだけ変えればよい
SHIPPING_RULES: list[tuple[int, int]] = [
    (5000, 0),
    (3000, 300),
    (0, 500),
]

# 商品種別 → 表示用ラベルのマッピング（在庫更新メッセージの表示に使用）
TYPE_LABELS: dict[str, str] = {
    "food": "食品",
    "electronics": "電子機器",
    "clothing": "衣料品",
    "books": "書籍",
}


# ---- ヘルパー関数 ----------------------------------------


def get_customer(customer_id: int) -> Optional[dict]:
    """顧客IDから顧客情報を取得する。存在しない場合は None を返す。"""
    return CUSTOMERS.get(customer_id)


def calculate_subtotal(items: list[dict]) -> int:
    """商品リストから小計を計算する。"""
    return sum(item["price"] * item["quantity"] for item in items)


def calculate_discount(subtotal: int, discount_code: str) -> int:
    """割引コードに応じた割引額を返す。該当なしは 0。"""
    rate = DISCOUNT_RATES.get(discount_code, 0.0)
    return int(subtotal * rate)


def calculate_shipping(subtotal: int) -> int:
    """小計に応じた送料を返す。"""
    for threshold, fee in SHIPPING_RULES:
        if subtotal >= threshold:
            return fee
    return 500  # フォールバック（SHIPPING_RULES が空の場合の保険）


def send_email(customer: dict, subject: str, body: str) -> None:
    """顧客にメールを送信する（本番ではメール送信APIを呼ぶ）。"""
    print(f"メール送信先: {customer['email']}")
    print(f"件名: {subject}")
    print(f"本文: {body}")


def update_inventory(items: list[dict]) -> None:
    """注文商品の在庫を減らす（本番ではDB更新APIを呼ぶ）。"""
    for item in items:
        label = TYPE_LABELS.get(item["type"], item["type"])
        print(f"{label} {item['name']} の在庫を{item['quantity']}個減らします")


# ---- メイン処理 ------------------------------------------


def process_order(customer_id: int, items: list[dict], discount_code: str = "") -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        raise ValueError(f"顧客ID {customer_id} が見つかりません")

    raw_subtotal = calculate_subtotal(items)
    discount = calculate_discount(raw_subtotal, discount_code)
    # 02の出力仕様に合わせ、"subtotal"は割引後の金額を表す
    subtotal = raw_subtotal - discount
    shipping = calculate_shipping(subtotal)
    total = subtotal + shipping

    send_email(
        customer,
        subject=f"ご注文確認 - 合計金額: {total}円",
        body=f"{customer['name']}様、ご注文ありがとうございます。合計金額は{total}円です。",
    )
    update_inventory(items)

    return {
        "customer_id": customer_id,
        "items": items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "status": "pending",
    }


def process_return(customer_id: int, items: list[dict], reason: str) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        raise ValueError(f"顧客ID {customer_id} が見つかりません")

    refund_amount = calculate_subtotal(items)

    send_email(
        customer,
        subject=f"返金処理完了 - 返金金額: {refund_amount}円",
        body=f"{customer['name']}様、返品を受け付けました。返金金額は{refund_amount}円です。",
    )

    return {
        "customer_id": customer_id,
        "refund_amount": refund_amount,
        "reason": reason,
        "status": "refunded",
    }


def check_order_status(customer_id: int, order_id: int) -> dict:
    customer = get_customer(customer_id)
    if customer is None:
        raise ValueError(f"顧客ID {customer_id} が見つかりません")

    status = "shipped"  # 実際はDB・外部APIから取得

    send_email(
        customer,
        subject="注文状況のお知らせ",
        body=f"{customer['name']}様、ご注文(ID:{order_id})の現在のステータス: {status}",
    )

    return {"order_id": order_id, "customer_id": customer_id, "status": status}


# ============================================================
# 動作確認
# ============================================================
if __name__ == "__main__":
    sample_items = [
        {"name": "りんご", "type": "food", "price": 200, "quantity": 3},
        {"name": "スマホケース", "type": "electronics", "price": 1500, "quantity": 1},
        {"name": "Tシャツ", "type": "clothing", "price": 2000, "quantity": 2},
    ]

    print("=== 注文処理 ===")
    order = process_order(1, sample_items, "GOLD10")
    print(order)

    print("\n=== 返品処理 ===")
    ret = process_return(2, sample_items[:1], "破損")
    print(ret)

    print("\n=== 注文状況確認 ===")
    result = check_order_status(1, 12345)
    print(result)

    print("\n=== エラーケース（存在しない顧客ID）===")
    try:
        process_order(999, sample_items, "")
    except ValueError as e:
        print(f"エラーを正常に検出: {e}")
