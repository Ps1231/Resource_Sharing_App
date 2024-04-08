from config import db
from queries import *
import mysql.connector
import re
with db.cursor() as cursor:
    cursor.execute("DESCRIBE Posts")
    enum_definition = cursor.fetchall()
#     # categories = [row['name'] for row in result]
#     # alter_query = f"ALTER TABLE Posts MODIFY category ENUM('{','.join(categories)}') DEFAULT NULL"
#     # categories = [row[1] for row in result]
#     # print(result)

#     def extract_categories(enum_definition):
#         categories_match = re.search(r"enum\((.*?)\)", enum_definition)
#         if categories_match:
#             categories_str = categories_match.group(1)
#             categories = [category.strip("'")
#                           for category in categories_str.split(',')]
#             return categories
#         else:
#             return None

#     def get_categories(cursor):
#         try:
#             cursor.execute("DESCRIBE Posts")
#             result = cursor.fetchall()
#             for row in result:
#                 if row['name'] == 'category':
#                     enum_definition = row[1]
#                     categories = extract_categories(enum_definition)
#                     return categories
#             else:
#                 print("Category column not found.")
#                 return None
#         except mysql.connector.Error as error:
#             print("Error:", error)
#             return None


# # Create cursor
#     cursor = db.cursor()

#     # Get categories
#     categories = get_categories(cursor)
#     print(categories)


# # cursor.execute("DESCRIBE posts")

# # # Fetch table description
# # table_description = cursor.fetchall()


# # def extract_categories(table_description):
# #     for field in table_description:
# #         if field[0] == 'category':
# #             enum_values = field[1]
# #             categories = enum_values[5:-1].replace("'", "").split(",")
# #             return categories
# #     return None


# # # Extract categories
# # categories = extract_categories(table_description)

# # print("Categories:", categories)

# # # Example usage:
# # # data = [{'Field': 'post_id', 'Type': 'int', 'Null': 'NO', 'Key': 'PRI', 'Default': None, 'Extra': 'auto_increment'}, {'Field': 'user_id', 'Type': 'int', 'Null': 'YES', 'Key': 'MUL', 'Default': None, 'Extra': ''}, {'Field': 'title', 'Type': 'varchar(255)', 'Null': 'YES', 'Key': '', 'Default': None, 'Extra': ''}, {'Field': 'body', 'Type': 'text', 'Null': 'YES', 'Key': '', 'Default': None, 'Extra': ''}, {'Field': 'create_date', 'Type': 'timestamp', 'Null': 'YES', 'Key': '', 'Default': None, 'Extra': ''}, {
# # #     'Field': 'deletion_date', 'Type': 'timestamp', 'Null': 'YES', 'Key': '', 'Default': None, 'Extra': ''}, {'Field': 'category', 'Type': "enum('Class Notes & Study Materials','Textbooks & References','Internship & Job Opportunities','Events & Hackathons','Study Groups & Tutoring','Online Courses tooo')", 'Null': 'YES', 'Key': '', 'Default': None, 'Extra': ''}, {'Field': 'post_views', 'Type': 'int', 'Null': 'YES', 'Key': '', 'Default': '0', 'Extra': ''}]


    def extract_categories():
        cursor.execute("DESCRIBE Posts")
        enum_definition = cursor.fetchall()
        categories = []
        for field in enum_definition:
            if field['Field'] == 'category':
                enum_values = field['Type']
                categories = enum_values[6:-2].replace("'", "").split(",")
                break
        return categories

    # Example usage:
    categories = extract_categories()
    if 'Online Courses tooo' in categories:
        categories.remove('Online Courses tooo')
    # categories.remove('Online Courses')
    print(categories)
