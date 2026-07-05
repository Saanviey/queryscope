


#given a question , embed it as a vector , compare to the table embeddings using cosine distances and find top k matches 
#question->vector->schema tables/columns/fks

def retrieve_tables(question :str , model ,conn , k :int =3):
       question_vector= model.encode(question).tolist() #encode to a vector
       vector_str= "[" + "," .join(str(x) for x in question_vector) +"]"  #convert to string

       cur= conn.cursor() #note - conn is just live connection string , curr obj is what does the actual talking
       
       #execute sql 
       cur.execute(
        """
        SELECT table_name, description, embedding <-> %s::vector AS distance
        FROM table_embeddings
        ORDER BY distance
        LIMIT %s
         """,
       (vector_str, k)
       )
       results = cur.fetchall()
       cur.close()
       return results
    
