from weni import Tool
from weni.context import Context
from weni.responses import TextResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import json
import random
import pytz


class InsertOrderData(Tool):
    def execute(self, context: Context) -> TextResponse:
        # Obter parâmetros do contexto
        prato = context.parameters.get("prato")
        cliente = context.parameters.get("cliente")
        
        try:
            # Validar parâmetros obrigatórios
            if not all([prato, cliente]):
                missing_params = []
                if not prato: missing_params.append("prato")
                if not cliente: missing_params.append("cliente")
                
                return TextResponse(data={
                    "error": f"Parâmetros obrigatórios faltando: {', '.join(missing_params)}",
                    "success": False
                })
            
            # Gerar data e hora automaticamente no horário de Brasília
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            now = datetime.now(brasilia_tz)
            data = now.strftime('%d/%m/%Y')
            hora = now.strftime('%H:%M')
            
            # Inserir pedido na planilha
            result = self.insert_order(prato, data, hora, cliente)
            
            return TextResponse(data=result)
            
        except Exception as e:
            error_result = {
                "error": f"Erro ao processar solicitação: {str(e)}",
                "success": False
            }
            return TextResponse(data=error_result)

    def _setup_connection(self):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        here = Path(__file__).resolve().parent   
        cred_path = here / "credentials.json"

        # fallback extra (se rodar de outro local)
        if not cred_path.exists():
            cred_path = Path.cwd() / "tools" / "insert_data" / "credentials.json"

        if not cred_path.exists():
            raise Exception(f"Credenciais não encontradas em: {cred_path}")

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            str(cred_path), scope
        )
        return gspread.authorize(credentials)


    def _generate_random_status(self) -> str:
        """Gera um status aleatório para o pedido"""
        status_options = ["Pronto", "Em Preparação", "Entregue"]
        return random.choice(status_options)

    def _generate_order_id(self) -> int:
        """Gera um ID único para o pedido"""
        try:
            # Setup connection
            client = self._setup_connection()
            SHEET_ID = "10Hb8zZqsHn8W2tSySFgPxZeHeP0e0JSc8NakdjGmUJI"
            SHEET_NAME = "Pedidos"
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            
            # Get all records to find the highest ID
            records = worksheet.get_all_records()
            
            if not records:
                # Se não há registros, começar com ID 1
                return 1
            
            # Encontrar o maior ID existente
            max_id = 0
            for record in records:
                try:
                    current_id = int(record.get('ID pedido', 0))
                    if current_id > max_id:
                        max_id = current_id
                except (ValueError, TypeError):
                    continue
            
            # Retornar o próximo ID
            return max_id + 1
            
        except Exception as e:
            # Se houver erro, usar timestamp como fallback (horário de Brasília)
            print(f"Erro ao gerar ID sequencial: {e}. Usando timestamp como fallback.")
            brasilia_tz = pytz.timezone('America/Sao_Paulo')
            return int(datetime.now(brasilia_tz).timestamp())

    def insert_order(self, prato: str, data: str, hora: str, cliente: str) -> Dict[str, Any]:
        """
        Insere um novo pedido na planilha
        
        Args:
            prato: Nome do prato
            data: Data no formato DD/MM/YYYY (gerada automaticamente)
            hora: Hora no formato HH:MM (gerada automaticamente)
            cliente: Nome do cliente
        
        Returns:
            Dictionary com resultado da inserção e ID gerado
        """
        try:
            # Setup connection
            client = self._setup_connection()
            SHEET_ID = "10Hb8zZqsHn8W2tSySFgPxZeHeP0e0JSc8NakdjGmUJI"
            SHEET_NAME = "Pedidos"
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            
            # Gerar ID único e status aleatório para o pedido
            order_id = self._generate_order_id()
            status = self._generate_random_status()
            
            # Preparar dados para inserção
            # Ordem das colunas: Prato, Data, Hora, Cliente, ID pedido, Status
            row_data = [prato, data, hora, cliente, order_id, status]
            
            # Inserir nova linha na planilha
            worksheet.append_row(row_data)
            
            # Preparar resposta de sucesso
            response = {
                "success": True,
                "message": f"Pedido registrado com sucesso!",
                "order_id": order_id,
                "order_data": {
                    "Prato": prato,
                    "Data": data,
                    "Hora": hora,
                    "Cliente": cliente,
                    "ID pedido": order_id,
                    "Status": status
                },
                "sheet_info": {
                    "sheet_id": SHEET_ID,
                    "sheet_name": SHEET_NAME
                }
            }
            
            print(f"Pedido {order_id} inserido com sucesso na planilha")
            
            return response
            
        except gspread.SpreadsheetNotFound:
            return {
                "error": f"Planilha não encontrada com ID: {SHEET_ID}",
                "success": False
            }
        except gspread.WorksheetNotFound:
            return {
                "error": f"Aba '{SHEET_NAME}' não encontrada na planilha",
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Erro ao inserir pedido: {str(e)}",
                "success": False
            }
