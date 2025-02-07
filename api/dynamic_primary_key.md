アプリケーションが主キーを知らない場合でもjdbcTemplateをつかって動的に主キーでソートするSQLを構築して実行することはできますか？

### **✅ JDBC Template を使って、アプリケーションが主キーを知らない場合でも動的に主キーでソートする SQL を実行する方法**

**結論:**  
**できます！** `INFORMATION_SCHEMA` や `sys.indexes` を使って、**指定されたテーブルの主キー（Primary Key）を動的に取得し、そのカラムを `ORDER BY` に使用する SQL を構築する** ことが可能です。

---

## **1. 手順の概要**
1. **対象のテーブルの主キーを取得**（`INFORMATION_SCHEMA` や `sys.indexes` を利用）
2. **取得した主キーを `ORDER BY` 句に組み込む**
3. **`JdbcTemplate` で動的に SQL を実行する**

---

## **2. 主キーを取得する SQL**
SQL Server では、`INFORMATION_SCHEMA.KEY_COLUMN_USAGE` を使うと、**指定されたテーブルの主キー情報を取得** できます。

```sql
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE TABLE_NAME = 'users' AND CONSTRAINT_NAME IN (
    SELECT CONSTRAINT_NAME
    FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
    WHERE TABLE_NAME = 'users' AND CONSTRAINT_TYPE = 'PRIMARY KEY'
);
```

📌 **ポイント**
- `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` から **主キーのカラム名** を取得
- **主キーが複数カラム（複合キー）の場合も考慮** できる

---

## **3. Spring Boot + `JdbcTemplate` で動的に SQL を構築する**
**📌 実装例: 指定されたテーブルの主キーを取得し、それを使って `ORDER BY` 付きの SQL を実行**

```java
package com.example.demo.service;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class DynamicQueryService {
    private final JdbcTemplate jdbcTemplate;

    public DynamicQueryService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * 指定されたテーブルの主キーを取得
     */
    public List<String> getPrimaryKeyColumns(String tableName) {
        String sql = """
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_NAME = ? AND CONSTRAINT_NAME IN (
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_NAME = ? AND CONSTRAINT_TYPE = 'PRIMARY KEY'
            )
        """;

        return jdbcTemplate.queryForList(sql, String.class, tableName, tableName);
    }

    /**
     * 指定されたテーブルの主キーでソートしてデータを取得
     */
    public List<Map<String, Object>> getSortedData(String tableName) {
        // 🔹 1. 主キーを取得
        List<String> primaryKeys = getPrimaryKeyColumns(tableName);

        if (primaryKeys.isEmpty()) {
            throw new IllegalArgumentException("テーブル " + tableName + " に主キーがありません");
        }

        // 🔹 2. ORDER BY 句を動的に作成（複数の主キーがある場合も考慮）
        String orderByClause = primaryKeys.stream().collect(Collectors.joining(", "));

        // 🔹 3. 動的に SQL を構築
        String sql = "SELECT * FROM " + tableName + " ORDER BY " + orderByClause;

        // 🔹 4. SQL 実行
        return jdbcTemplate.queryForList(sql);
    }
}
```

---

## **4. Spring Boot の Controller で API を作成**
```java
package com.example.demo.controller;

import com.example.demo.service.DynamicQueryService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/data")
public class DynamicQueryController {
    private final DynamicQueryService queryService;

    public DynamicQueryController(DynamicQueryService queryService) {
        this.queryService = queryService;
    }

    @GetMapping("/{tableName}")
    public Map<String, Object> getDataSortedByPrimaryKey(@PathVariable String tableName) {
        List<Map<String, Object>> data = queryService.getSortedData(tableName);
        return Map.of("status", "success", "data", data);
    }
}
```

---

## **5. 動作確認**
### **📌 テストデータ**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

INSERT INTO users (id, name, age) VALUES (3, 'C', 30);
INSERT INTO users (id, name, age) VALUES (1, 'A', 25);
INSERT INTO users (id, name, age) VALUES (2, 'B', 28);
```

### **📌 API を実行**
```sh
curl -X GET "http://localhost:8080/api/data/users"
```
📌 **レスポンス**
```json
{
  "status": "success",
  "data": [
    { "id": 1, "name": "A", "age": 25 },
    { "id": 2, "name": "B", "age": 28 },
    { "id": 3, "name": "C", "age": 30 }
  ]
}
```

✅ **主キー（`id`）でソートされて取得されている！**

---

## **6. セキュリティ対策**
**⚠️ `tableName` を直接 SQL に埋め込むのは危険（SQL インジェクションのリスクあり）**  
→ **ホワイトリストを用意して、許可されたテーブルのみアクセス可能にする！**
```java
List<String> allowedTables = List.of("users", "orders");
if (!allowedTables.contains(tableName)) {
    throw new IllegalArgumentException("許可されていないテーブルです");
}
```

---

## **7. まとめ**
✅ **JDBC Template を使って、アプリが主キーを知らなくても動的にソート可能！**  
✅ **`INFORMATION_SCHEMA.KEY_COLUMN_USAGE` から主キーを取得し、`ORDER BY` に利用**  
✅ **Spring Boot の `JdbcTemplate` を活用して、柔軟なデータ取得 API を実装**  
✅ **SQL インジェクションを防ぐため、ホワイトリストでテーブル名を制限するのが重要！**  

🚀 **この方法を使えば、どのテーブルに対しても「主キー順にソートされたデータ」を取得する汎用 API を作れます！** 🎯