import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import time

def calc_dist(vec1, vec2):
    dist = 0.0
    #print(len(vec1))
    dist = 0
    for i in range(len(vec1)):
        dist+= (vec1[i]-vec2[i])**2
    dist = dist/len(vec1)
    return dist
    

def lambda_handler(event, context):
    
    dynamodb = boto3.resource("dynamodb")
    blog_table = dynamodb.Table("blogs-db")
    blogs_list = (blog_table.scan())["Items"]
    blog_ids_list = []
    blog_math_vectors_list = []
    is_deleted_list = []
    for cur_dict in blogs_list:
        blog_ids_list.append(cur_dict["blog_id"])
        blog_math_vectors_list.append(cur_dict["math_vector"])
        is_deleted_list.append(cur_dict["deleted"]) 
    put_table = dynamodb.Table('related-blogs-db')
    with put_table.batch_writer() as batch:
        for i in range(len(blog_ids_list)):
            if is_deleted_list[i]==True:
                continue
            possible_candidates = []
            for j in range(len(blog_ids_list)):
                if is_deleted_list[j] ==True or i == j:
                    continue
                dist = calc_dist(blog_math_vectors_list[i], blog_math_vectors_list[j])
                possible_candidates.append([dist, blog_ids_list[j]])
            possible_candidates.sort(key=lambda x: x[0])
            related_blogs = []
            for j in range(10):
                related_blogs.append(possible_candidates[j][1][:])
            new_record = {
                "blog_id" : blog_ids_list[i],
                "related_blogs_ids": related_blogs
            }
            batch.put_item(Item=new_record)
            time.sleep(1)
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully updated related-blogs-db')
    }
