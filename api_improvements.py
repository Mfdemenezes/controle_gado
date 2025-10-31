"""
Melhorias para API v2.0:
- Endpoints PUT para edição
- Tratamento de erro padronizado
- Validações melhores
"""

# Decorador para tratamento de erro
def handle_db_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except psycopg2.Error as e:
            raise HTTPException(
                status_code=400,
                detail={"error": "Erro no banco de dados", "message": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail={"error": "Erro interno", "message": str(e)}
            )
    return wrapper

# Endpoints PUT para adicionar:

# PUT /api/racas/{id}
@app.put("/api/racas/{raca_id}", tags=["🧬 Raças"])
async def atualizar_raca(raca_id: int, nome: Optional[str] = None, 
                         descricao: Optional[str] = None, 
                         origem: Optional[str] = None,
                         ativo: Optional[bool] = None):
    """Atualizar raça existente"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Montar query dinâmica
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if descricao is not None:
            updates.append("descricao = %s")
            params.append(descricao)
        if origem is not None:
            updates.append("origem = %s")
            params.append(origem)
        if ativo is not None:
            updates.append("ativo = %s")
            params.append(ativo)
        
        if not updates:
            raise HTTPException(400, detail="Nenhum campo para atualizar")
        
        params.append(raca_id)
        query = f"""
            UPDATE racas 
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """
        cur.execute(query, params)
        raca = cur.fetchone()
        
        if not raca:
            raise HTTPException(404, detail="Raça não encontrada")
        
        conn.commit()
        return dict(raca)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()

# PUT /api/touros/{id}
@app.put("/api/touros/{touro_id}", tags=["🐂 Touros"])
async def atualizar_touro(touro_id: int, nome: Optional[str] = None,
                          raca_id: Optional[int] = None,
                          ativo: Optional[bool] = None,
                          observacoes: Optional[str] = None):
    """Atualizar touro existente"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        updates = []
        params = []
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if raca_id is not None:
            updates.append("raca_id = %s")
            params.append(raca_id)
        if ativo is not None:
            updates.append("ativo = %s")
            params.append(ativo)
        if observacoes is not None:
            updates.append("observacoes = %s")
            params.append(observacoes)
        
        if not updates:
            raise HTTPException(400, detail="Nenhum campo para atualizar")
        
        params.append(touro_id)
        query = f"""
            UPDATE touros 
            SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING *
        """
        cur.execute(query, params)
        touro = cur.fetchone()
        
        if not touro:
            raise HTTPException(404, detail="Touro não encontrado")
        
        conn.commit()
        return dict(touro)
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()

# DELETE endpoints também

@app.delete("/api/racas/{raca_id}", tags=["🧬 Raças"])
async def deletar_raca(raca_id: int):
    """Desativar raça (soft delete)"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE racas SET ativo = false WHERE id = %s RETURNING id", (raca_id,))
        if not cur.fetchone():
            raise HTTPException(404, detail="Raça não encontrada")
        conn.commit()
        return {"message": "Raça desativada com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, detail={"error": str(e)})
    finally:
        cur.close()
        conn.close()
