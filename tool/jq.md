標準入力からのjsonを解析できるようにしてください

**標準入力（stdin）からJSONを解析できるように改良したバージョン** を作成しました。  
これにより、`cat data.json | java JsonQueryTool "$.name"` のようにパイプでJSONデータを渡すことができます。

---

## **修正ポイント**
- **標準入力からJSONを受け取る**  
  - `System.in` を使用して JSON データを読み込む  
- **ファイルまたは標準入力を自動判別**  
  - `args[0]` に `"-"` を指定すると、標準入力を使用する  
- **エラーハンドリングを強化**

---

## **修正後の Java コード**
```java
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jayway.jsonpath.JsonPath;

import java.io.*;

public class JsonQueryTool {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java JsonQueryTool <query> [json-file]");
            System.out.println("Example with file: java JsonQueryTool \"$.name\" data.json");
            System.out.println("Example with stdin: cat data.json | java JsonQueryTool \"$.name\" -");
            System.exit(1);
        }

        String query = args[0];  // クエリ
        String jsonSource = (args.length > 1) ? args[1] : "-"; // JSONの入力元（ファイル or 標準入力）

        try {
            // JSONを読み込む
            String json = readJson(jsonSource);

            // JSONPathでクエリを適用
            Object result = JsonPath.read(json, query);

            // 結果を出力
            ObjectMapper objectMapper = new ObjectMapper();
            String formattedJson = objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(result);
            System.out.println(formattedJson);

        } catch (IOException e) {
            System.err.println("Error reading JSON: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Error processing query: " + e.getMessage());
        }
    }

    /**
     * JSONをファイルまたは標準入力から読み込む
     */
    private static String readJson(String source) throws IOException {
        InputStream inputStream;
        
        if ("-".equals(source)) {
            inputStream = System.in; // 標準入力から読み込む
        } else {
            inputStream = new FileInputStream(new File(source)); // ファイルから読み込む
        }

        // JSONデータをStringに変換
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            StringBuilder jsonBuilder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                jsonBuilder.append(line);
            }
            return jsonBuilder.toString();
        }
    }
}
```

---

## **使い方**
### **1. ファイルからJSONを取得**
```sh
java JsonQueryTool "$.name" data.json
```
**出力:**
```json
"Alice"
```

---

### **2. 標準入力（stdin）からJSONを取得**
```sh
cat data.json | java JsonQueryTool "$.name" -
```
または：
```sh
echo '{"name": "Alice", "age": 25}' | java JsonQueryTool "$.name" -
```
**出力:**
```json
"Alice"
```

---

### **3. 配列データの取得**
```sh
echo '{"skills": [{"language": "Java"}, {"language": "Python"}]}' | java JsonQueryTool "$.skills[*].language" -
```
**出力:**
```json
[
  "Java",
  "Python"
]
```

---

## **改良点**
✅ **標準入力（stdin）対応** (`"-"` を指定するとstdinからJSONを読み込む)  
✅ **ファイルと標準入力の両方をサポート**  
✅ **エラーハンドリングを強化**  
✅ **シンプルな構成で拡張しやすい**

💡 **これで `jq` のように標準入力やファイルのJSONを解析できるようになりました！** 🚀