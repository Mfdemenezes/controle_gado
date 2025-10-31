# Este código deve ser adicionado ao api_gado.py

# ===== LOTES - CRUD COMPLETO =====
@app.post("/api/lotes", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_lote(nome: str, descricao: Optional[str] = None, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO lotes (nome, descricao) VALUES (%s, %s) RETURNING id, nome, descricao, ativo",
            (nome, descricao)
        )
        lote = cur.fetchone()
        conn.commit()
        return dict(lote)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def obter_lote(lote_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM lotes WHERE id = %s", (lote_id,))
        lote = cur.fetchone()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        return dict(lote)
    finally:
        cur.close()
        conn.close()

@app.put("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def atualizar_lote(lote_id: int, nome: Optional[str] = None, descricao: Optional[str] = None, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(lote_id)
        query = f"UPDATE lotes SET {', '.join(updates)} WHERE id = %s RETURNING *"
        cur.execute(query, params)
        lote = cur.fetchone()
        if not lote:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        conn.commit()
        return dict(lote)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/api/lotes/{lote_id}", tags=["📍 Lotes e Pastos"])
async def deletar_lote(lote_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE lotes SET ativo = false WHERE id = %s RETURNING id", (lote_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Lote não encontrado")
        conn.commit()
        return {"message": "Lote excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

# ===== PASTOS - CRUD COMPLETO =====
@app.post("/api/pastos", tags=["📍 Lotes e Pastos"], status_code=status.HTTP_201_CREATED)
async def criar_pasto(nome: str, area_hectares: Optional[float] = None, tipo_pasto: Optional[str] = None, descricao: Optional[str] = None, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            "INSERT INTO pastos (nome, area_hectares, tipo_pasto, descricao) VALUES (%s, %s, %s, %s) RETURNING *",
            (nome, area_hectares, tipo_pasto, descricao)
        )
        pasto = cur.fetchone()
        conn.commit()
        return dict(pasto)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.get("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def obter_pasto(pasto_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM pastos WHERE id = %s", (pasto_id,))
        pasto = cur.fetchone()
        if not pasto:
            raise HTTPException(status_code=404, detail="Pasto não encontrado")
        return dict(pasto)
    finally:
        cur.close()
        conn.close()

@app.put("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def atualizar_pasto(pasto_id: int, nome: Optional[str] = None, area_hectares: Optional[float] = None, tipo_pasto: Optional[str] = None, descricao: Optional[str] = None, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if area_hectares is not None:
            updates.append("area_hectares = %s")
            params.append(area_hectares)
        if tipo_pasto is not None:
            updates.append("tipo_pasto = %s")
            params.append(tipo_pasto)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        
        if not updates:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        params.append(pasto_id)
        query = f"UPDATE pastos SET {', '.join(updates)} WHERE id = %s RETURNING *"
        cur.execute(query, params)
        pasto = cur.fetchone()
        if not pasto:
            raise HTTPException(status_code=404, detail="Pasto não encontrado")
        conn.commit()
        return dict(pasto)
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/api/pastos/{pasto_id}", tags=["📍 Lotes e Pastos"])
async def deletar_pasto(pasto_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE pastos SET ativo = false WHERE id = %s RETURNING id", (pasto_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pasto não encontrado")
        conn.commit()
        return {"message": "Pasto excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.delete("/api/touros/{touro_id}", tags=["🐂 Touros"])
async def deletar_touro(touro_id: int, user_data: dict = Depends(verify_token)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE touros SET ativo = false WHERE id = %s RETURNING id", (touro_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Touro não encontrado")
        conn.commit()
        return {"message": "Touro excluído com sucesso"}
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
