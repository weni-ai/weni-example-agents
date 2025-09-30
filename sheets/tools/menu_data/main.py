from weni import Tool
from weni.context import Context
from weni.responses import TextResponse
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import Dict, Any, List
from pathlib import Path
import json


class GetMenuData(Tool):
    def execute(self, context: Context) -> TextResponse:
        # Obter parâmetros do contexto
        categoria = context.parameters.get("categoria")
        busca = context.parameters.get("busca")
        
        try:
            if categoria:
                # Buscar pratos por categoria específica
                result = self.get_pratos_por_categoria(categoria)
            elif busca:
                # Buscar pratos por nome/descrição
                result = self.buscar_pratos(busca)
            else:
                # Listar todas as categorias e pratos
                result = self.get_cardapio_completo()
            
            return TextResponse(data=result)
            
        except Exception as e:
            error_result = {
                "error": f"Erro ao consultar cardápio: {str(e)}",
                "data": []
            }
            return TextResponse(data=error_result)

    def _setup_connection(self):
        """Configura conexão com Google Sheets"""
        scope = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        here = Path(__file__).resolve().parent   
        cred_path = here / "credentials.json"

        # fallback extra (se rodar de outro local)
        if not cred_path.exists():
            cred_path = Path.cwd() / "tools" / "menu_data" / "credentials.json"

        if not cred_path.exists():
            raise Exception(f"Credenciais não encontradas em: {cred_path}")

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            str(cred_path), scope
        )
        return gspread.authorize(credentials)

    def _load_cardapio(self) -> List[Dict[str, Any]]:
        """Carrega o cardápio da planilha Google Sheets"""
        try:
            client = self._setup_connection()
            SHEET_ID = "10Hb8zZqsHn8W2tSySFgPxZeHeP0e0JSc8NakdjGmUJI"
            SHEET_NAME = "Pratos"
            
            # Open the spreadsheet
            spreadsheet = client.open_by_key(SHEET_ID)
            worksheet = spreadsheet.worksheet(SHEET_NAME)
            
            # Get all records
            records = worksheet.get_all_records()
            
            return records
            
        except Exception as e:
            raise Exception(f"Erro ao carregar cardápio da planilha: {str(e)}")

    def get_cardapio_completo(self) -> Dict[str, Any]:
        """
        Retorna o cardápio completo com todos os pratos da planilha
        
        Returns:
            Dictionary com cardápio completo organizado por categorias
        """
        try:
            pratos = self._load_cardapio()
            
            if not pratos:
                return {
                    "message": "Nenhum prato encontrado na planilha",
                    "total_pratos": 0,
                    "pratos": []
                }
            
            # Organizar pratos por categoria
            categorias = {}
            for prato in pratos:
                categoria = prato.get('Categoria', 'Outros')
                if categoria not in categorias:
                    categorias[categoria] = []
                categorias[categoria].append(prato)
            
            # Preparar resposta organizada
            categorias_info = []
            for categoria, pratos_categoria in categorias.items():
                categorias_info.append({
                    "categoria": categoria,
                    "quantidade_pratos": len(pratos_categoria),
                    "pratos": pratos_categoria
                })
            
            return {
                "message": f"Cardápio completo com {len(pratos)} pratos em {len(categorias)} categorias",
                "total_pratos": len(pratos),
                "total_categorias": len(categorias),
                "categorias": categorias_info
            }
            
        except Exception as e:
            return {
                "error": f"Erro ao carregar cardápio completo: {str(e)}",
                "data": []
            }

    def get_pratos_por_categoria(self, categoria: str) -> Dict[str, Any]:
        """
        Busca pratos por categoria específica
        
        Args:
            categoria: Nome da categoria
        
        Returns:
            Dictionary com pratos da categoria especificada
        """
        try:
            pratos = self._load_cardapio()
            categoria_lower = categoria.lower().strip()
            
            # Filtrar pratos por categoria
            pratos_filtrados = []
            categorias_disponiveis = set()
            
            for prato in pratos:
                prato_categoria = prato.get('Categoria', '').lower()
                categorias_disponiveis.add(prato.get('Categoria', 'Outros'))
                
                if categoria_lower in prato_categoria or prato_categoria == categoria_lower:
                    pratos_filtrados.append(prato)
            
            if not pratos_filtrados:
                return {
                    "message": f"Categoria '{categoria}' não encontrada ou sem pratos",
                    "categorias_disponiveis": list(categorias_disponiveis),
                    "data": []
                }
            
            return {
                "message": f"Pratos da categoria '{categoria}' - {len(pratos_filtrados)} encontrado(s)",
                "categoria": categoria,
                "total_pratos": len(pratos_filtrados),
                "pratos": pratos_filtrados
            }
            
        except Exception as e:
            return {
                "error": f"Erro ao buscar categoria: {str(e)}",
                "data": []
            }

    def buscar_pratos(self, busca: str) -> Dict[str, Any]:
        """
        Busca pratos por nome ou descrição
        
        Args:
            busca: Termo de busca
        
        Returns:
            Dictionary com pratos encontrados
        """
        try:
            pratos = self._load_cardapio()
            busca_lower = busca.lower().strip()
            pratos_encontrados = []
            
            for prato in pratos:
                # Buscar no nome do prato ou descrição
                nome_prato = prato.get('Nome do Prato', '').lower()
                descricao = prato.get('Descrição', '').lower()
                
                if (busca_lower in nome_prato or busca_lower in descricao):
                    pratos_encontrados.append(prato)
            
            if not pratos_encontrados:
                return {
                    "message": f"Nenhum prato encontrado para '{busca}'",
                    "sugestao": "Tente buscar por nome do prato ou ingredientes da descrição",
                    "data": []
                }
            
            return {
                "message": f"Encontrados {len(pratos_encontrados)} prato(s) para '{busca}'",
                "termo_busca": busca,
                "total_encontrados": len(pratos_encontrados),
                "pratos": pratos_encontrados
            }
            
        except Exception as e:
            return {
                "error": f"Erro ao buscar pratos: {str(e)}",
                "data": []
            }

    def get_categorias_disponiveis(self) -> List[str]:
        """Retorna lista de categorias disponíveis"""
        try:
            pratos = self._load_cardapio()
            categorias = set()
            for prato in pratos:
                categoria = prato.get('Categoria', 'Outros')
                if categoria:
                    categorias.add(categoria)
            return list(categorias)
        except Exception:
            return []
