from weni import Tool
from weni.context import Context
from weni.responses import TextResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import json
import sys



class GetOrderData(Tool):
    def execute(self, context: Context) -> TextResponse:
        """Método principal executado pelo agente"""
        # Obter parâmetros do contexto
        order_id = context.parameters.get("order_id")
        
        try:
            if order_id:
                # Buscar pedido específico por ID
                result = self.get_order_by_id(order_id)
            else:
                # Listar todos os pedidos
                result = self.get_all_orders()
            
            # Calcular tamanho da resposta
            s = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
            size_bytes = len(s.encode("utf-8"))
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            
            print(f"\n📊 TAMANHO DA RESPOSTA: {size_bytes:,} B | {size_kb:.2f} KB | {size_mb:.4f} MB")
            
            return TextResponse(data=result)
            
        except Exception as e:
            error_result = {
                "error": f"Erro ao processar solicitação: {str(e)}",
                "data": []
            }
            return TextResponse(data=error_result)

    def _setup_connection(self):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        here = Path(__file__).resolve().parent   
        cred_path = here / "credentials.json"

        # fallback extra (se rodar de outro local)
        if not cred_path.exists():
            cred_path = Path.cwd() / "tools" / "get_data" / "credentials.json"

        if not cred_path.exists():
            raise Exception(f"Credenciais não encontradas em: {cred_path}")

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            str(cred_path), scope
        )
        return gspread.authorize(credentials)

    def get_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """
        Busca um pedido específico por ID
        
        Args:
            order_id: ID do pedido a ser buscado
        
        Returns:
            Dictionary com os dados do pedido encontrado (Prato, Data, Hora, Cliente, ID pedido, Status)
        """
        try:
            # Setup connection
            client = self._setup_connection()
            SHEET_ID = "10Hb8zZqsHn8W2tSySFgPxZeHeP0e0JSc8NakdjGmUJI"
            SHEET_NAME = "Pedidos"
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            
            # Get all records
            records = worksheet.get_all_records()
            
            if not records:
                return {
                    "message": "Nenhum pedido encontrado na planilha",
                    "data": None,
                    "found": False
                }
            
            # Buscar pedido por ID
            for record in records:
                if str(record.get('ID pedido', '')) == str(order_id):
                    return {
                        "message": f"Pedido {order_id} encontrado com sucesso",
                        "data": record,
                        "found": True
                    }
            
            # Se chegou aqui, não encontrou o pedido
            return {
                "message": f"Pedido com ID {order_id} não foi encontrado",
                "data": None,
                "found": False,
                "total_orders_in_sheet": len(records)
            }
            
        except gspread.SpreadsheetNotFound:
            return {
                "error": f"Planilha não encontrada com ID: {SHEET_ID}",
                "data": None,
                "found": False
            }
        except gspread.WorksheetNotFound:
            return {
                "error": f"Aba '{SHEET_NAME}' não encontrada na planilha",
                "data": None,
                "found": False
            }
        except Exception as e:
            return {
                "error": f"Erro ao buscar pedido: {str(e)}",
                "data": None,
                "found": False
            }

    def get_all_orders(self) -> Dict[str, Any]:
        """
        Recupera todos os pedidos da planilha
        
        Returns:
            Dictionary com todos os pedidos e metadados (inclui Prato, Data, Hora, Cliente, ID pedido, Status)
        """
        try:
            # Setup connection
            client = self._setup_connection()
            SHEET_ID = "10Hb8zZqsHn8W2tSySFgPxZeHeP0e0JSc8NakdjGmUJI"
            SHEET_NAME = "Pedidos"
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            
            # Get all records
            records = worksheet.get_all_records()
            
            if not records:
                return {
                    "message": "Nenhum pedido encontrado na planilha",
                    "data": [],
                    "total_orders": 0
                }
            
            # Prepare response
            response = {
                "message": f"Encontrados {len(records)} pedido(s) na planilha",
                "data": records,
                "total_orders": len(records),
            }
            
            print(f"Recuperados {len(records)} pedido(s) da planilha")
            
            return response
            
        except gspread.SpreadsheetNotFound:
            return {
                "error": f"Planilha não encontrada com ID: {SHEET_ID}",
                "data": []
            }
        except gspread.WorksheetNotFound:
            return {
                "error": f"Aba '{SHEET_NAME}' não encontrada na planilha",
                "data": []
            }
        except Exception as e:
            return {
                "error": f"Erro ao processar dados: {str(e)}",
                "data": []
            }

