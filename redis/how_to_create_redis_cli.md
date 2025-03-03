Embedded-redisをスタンドアロンで起動しています。このサーバーに接続して簡単なコマンドを送信できるRedis-cliのようなものをJavaで作るにはどうしたらいいですか？

**JavaでEmbedded-Redisに接続し、Redis-cliのようにコマンドを送信できるシンプルなクライアントを作る方法** を紹介します。

---

## **方法**
### **1. Jedisを使ってRedisに接続**
**Jedis** は、Redisと通信するためのシンプルなJavaクライアントライブラリです。  
これを使えば、Embedded-Redisのサーバーに接続し、CLIのようにコマンドを送信できます。

### **2. コンソール入力を受け取り、コマンドをRedisに送信**
`Scanner` を使ってユーザー入力を受け付け、JedisでRedisにコマンドを送信します。

---

## **実装**
### **1. 必要な依存関係（Gradleの場合）**
```gradle
dependencies {
    implementation 'redis.clients:jedis:5.1.0'
}
```

### **2. Javaプログラム**
```java
import redis.clients.jedis.Jedis;

import java.util.Scanner;

public class RedisCliJava {
    public static void main(String[] args) {
        // Embedded Redis のサーバーに接続（ポートは適宜変更）
        String redisHost = "localhost";
        int redisPort = 6379;
        
        try (Jedis jedis = new Jedis(redisHost, redisPort);
             Scanner scanner = new Scanner(System.in)) {

            System.out.println("Connected to Redis at " + redisHost + ":" + redisPort);
            System.out.println("Type Redis commands (or type 'exit' to quit):");

            while (true) {
                System.out.print("redis> ");
                String input = scanner.nextLine().trim();

                if ("exit".equalsIgnoreCase(input)) {
                    System.out.println("Exiting...");
                    break;
                }

                try {
                    String[] parts = input.split(" ");
                    String command = parts[0].toUpperCase();
                    String result;

                    switch (command) {
                        case "SET":
                            if (parts.length == 3) {
                                result = jedis.set(parts[1], parts[2]);
                            } else {
                                result = "Usage: SET key value";
                            }
                            break;
                        case "GET":
                            if (parts.length == 2) {
                                result = jedis.get(parts[1]);
                            } else {
                                result = "Usage: GET key";
                            }
                            break;
                        case "DEL":
                            if (parts.length >= 2) {
                                result = String.valueOf(jedis.del(parts[1]));
                            } else {
                                result = "Usage: DEL key";
                            }
                            break;
                        case "KEYS":
                            result = jedis.keys("*").toString();
                            break;
                        default:
                            result = "Unsupported command";
                    }

                    System.out.println(result);

                } catch (Exception e) {
                    System.out.println("Error executing command: " + e.getMessage());
                }
            }
        }
    }
}
```

---

## **動作例**
```sh
$ java RedisCliJava
Connected to Redis at localhost:6379
Type Redis commands (or type 'exit' to quit):
redis> SET mykey Hello
OK
redis> GET mykey
Hello
redis> KEYS *
[mykey]
redis> DEL mykey
1
redis> GET mykey
null
redis> exit
Exiting...
```

---

## **ポイント**
1. **Jedisを使用**してRedisに接続
2. **ユーザー入力を受け付け**、Redisコマンドとして処理
3. **簡単なコマンド（SET, GET, DEL, KEYS）に対応**
4. **エラーハンドリング**を実装（不正なコマンド時にメッセージを出す）

---

### **発展**
- すべてのRedisコマンドに対応するように拡張
- `JedisPooled` を使って接続プールを利用
- **Spring Boot + Redis** でWebアプリとして作成

この方法で、簡単な **Redis CLI for Java** を作れます！  
**試してみて、動作を確認してみてください！** 🚀