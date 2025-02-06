LIKE検索のようなことをできるようにする場合、どのようにURIを設計すればいいでしょうか？

**LIKE 検索（部分一致検索）** を API で実現する場合、**RESTful API の設計方針**に従いながら、適切なクエリパラメータを活用するのが一般的です。

---

## **1. クエリパラメータを使う方法（推奨）**
REST の原則に従い、`GET` リクエストで **検索条件をクエリパラメータとして指定** します。

### **例: ユーザー名の部分一致検索**
```plaintext
GET /users?name_like=tanaka
```

### **具体的な設計例**
| パラメータ | 説明 |
|-----------|------|
| `name_like` | ユーザー名が "tanaka" を含むデータを検索 |
| `email_like` | メールアドレスに特定の文字列が含まれるものを検索 |

🔹 `_like` のようなサフィックスを付けることで、「部分一致検索である」ことを明示できます。

---

## **2. 検索専用のエンドポイントを作る**
検索が頻繁に行われる場合、検索専用のエンドポイントを作成するのも一つの方法です。

### **例:**
```plaintext
GET /users/search?name=tanaka
```
または
```plaintext
GET /search/users?name=tanaka
```
こうすると、通常の `GET /users` と区別がしやすくなります。

---

## **3. パスパラメータを使う方法（非推奨）**
REST の設計上、**検索条件はリソースの一部ではないため、パスパラメータでの検索は非推奨**です。

**NG の例**
```plaintext
GET /users/name/tanaka
```
この設計では、"tanaka" という名前の固定リソースを取得する意味に見えてしまい、REST の原則に反します。

---

## **4. 検索の方法を指定できるようにする**
検索方法を拡張する場合、`match` のようなパラメータを追加するのもありです。

### **例:**
```plaintext
GET /users?name=tanaka&match=like
```

| `match` の値 | 説明 |
|-------------|------|
| `exact` | 完全一致 (`=`) |
| `like` | 部分一致 (`LIKE %xxx%`) |
| `startswith` | 前方一致 (`LIKE xxx%`) |
| `endswith` | 後方一致 (`LIKE %xxx`) |

---

## **5. GraphQL を使う場合**
GraphQL では単一エンドポイント (`/graphql`) にクエリを送信するため、柔軟な検索が可能です。

**例**
```graphql
{
  users(filter: { name_contains: "tanaka" }) {
    id
    name
    email
  }
}
```

---

## **結論（推奨パターン）**
| 設計方法 | 使いやすさ | RESTful 準拠 | 例 |
|---------|---------|------------|---|
| **✅ クエリパラメータ方式（推奨）** | ◎ | ◎ | `GET /users?name_like=tanaka` |
| 🔹 **検索専用エンドポイント** | 〇 | ◎ | `GET /users/search?name=tanaka` |
| ❌ **パスパラメータ方式（非推奨）** | △ | ❌ | `GET /users/name/tanaka` |
| ✅ **検索方法を拡張（オプション付き）** | ◎ | ◎ | `GET /users?name=tanaka&match=like` |

---

## **どの方法を選ぶべきか？**
- **シンプルな部分一致検索** → `GET /users?name_like=tanaka`
- **高度な検索をサポートしたい** → `GET /users?name=tanaka&match=like`
- **検索条件が多く、複雑なクエリになる** → `GET /users/search?name=tanaka`
- **GraphQL を導入している場合** → `users(filter: { name_contains: "tanaka" })`

このような API 設計を考えることで、使いやすく拡張性のある設計ができます！ 🚀