# api2d-MySQL-Context
使用API2D实现基于mysql的持久化、无需维护的对话上下文

和我的另一个项目一样，通过简单的代码实现基于conversation_id和parent_massage_id的上下文，
让应用端可以更简单的使用api2d，无需在本地维护上下文，同时利用mysql可以实现更加持久的上下文记录和保存
这是一个简单的py代码，欢迎fork开发更加完善的版本

使用前请简单阅读代码，修改代码中的数据库地址，数据库密码，以及第119行左右填入你的api2d的token
以下是需要建立的数据库表字段，
MYSQL_DATABASE_CHARSET需要是utf8mb4（储存chagpt返回的emoji）
```
CREATE TABLE conversations (
     id VARCHAR(255) PRIMARY KEY
 );
```
```
 CREATE TABLE messages (
     id VARCHAR(255) PRIMARY KEY,
     conversation_id VARCHAR(255),
     parent_message_id VARCHAR(255),
     text TEXT NOT NULL,
     role ENUM('user', 'assistant') NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     FOREIGN KEY (conversation_id) REFERENCES conversations(id),
     FOREIGN KEY (parent_message_id) REFERENCES messages(id)
 );
 ```
