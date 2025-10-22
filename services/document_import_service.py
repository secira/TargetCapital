"""
Document Import Service using RAG + LLM
Intelligently parse and extract holdings data from PDFs, Excel files, and broker statements
"""

import os
import logging
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DocumentImportService:
    """
    Service to import holdings from various document formats using RAG + LLM
    
    Architecture:
    1. Document Parsing: Extract text/tables from PDFs/Excel
    2. Context Building: Create structured context with field mappings
    3. LLM Processing: Use GPT-4 to intelligently map and extract data
    4. Validation: Verify extracted data against schema
    5. Database Import: Insert validated records
    """
    
    def __init__(self):
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
    def import_excel_file(self, file_path: str, asset_class: str, user_id: int) -> Dict[str, Any]:
        """
        Import holdings from Excel file using LLM to intelligently map columns
        
        Args:
            file_path: Path to uploaded Excel file
            asset_class: Type of asset (equities, mutual_funds, etc.)
            user_id: User ID for ownership
            
        Returns:
            Dict with success status, count, and imported records
        """
        try:
            # Step 1: Read Excel file
            df = pd.read_excel(file_path)
            
            # Step 2: Get schema template for asset class
            schema = self._get_asset_schema(asset_class)
            
            # Step 3: Use LLM to map Excel columns to schema fields
            column_mapping = self._map_columns_with_llm(
                excel_columns=df.columns.tolist(),
                target_schema=schema,
                asset_class=asset_class
            )
            
            # Step 4: Extract and transform data
            records = self._extract_records_from_excel(df, column_mapping, schema)
            
            # Step 5: Validate records
            validated_records = self._validate_records(records, asset_class)
            
            # Step 6: Import to database
            imported_count = self._import_to_database(validated_records, asset_class, user_id)
            
            return {
                'success': True,
                'count': imported_count,
                'records': validated_records,
                'mapping': column_mapping
            }
            
        except Exception as e:
            logger.error(f"Error importing Excel file: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def import_pdf_statement(self, file_path: str, asset_class: str, user_id: int, 
                            statement_type: str = 'broker') -> Dict[str, Any]:
        """
        Import holdings from PDF statement using RAG + LLM for intelligent parsing
        
        This uses a multi-stage RAG approach:
        1. Extract text from PDF (using PyPDF2 or pdfplumber)
        2. Chunk text into semantic sections
        3. Use vector embeddings to find relevant data sections
        4. Use LLM to extract structured data from relevant sections
        
        Args:
            file_path: Path to PDF file
            asset_class: Type of asset
            user_id: User ID
            statement_type: Type of statement (broker, bank, demat, cas)
            
        Returns:
            Dict with import results
        """
        try:
            # Step 1: Extract text from PDF
            pdf_text = self._extract_pdf_text(file_path)
            
            # Step 2: Create semantic chunks
            chunks = self._chunk_pdf_text(pdf_text)
            
            # Step 3: Generate embeddings for chunks (RAG component)
            chunk_embeddings = self._generate_embeddings(chunks)
            
            # Step 4: Create query embeddings for relevant data
            query_embeddings = self._generate_query_embeddings(asset_class, statement_type)
            
            # Step 5: Retrieve most relevant chunks using vector similarity
            relevant_chunks = self._retrieve_relevant_chunks(
                chunk_embeddings, 
                query_embeddings,
                chunks
            )
            
            # Step 6: Use LLM to extract structured data from relevant chunks
            extracted_data = self._extract_holdings_with_llm(
                relevant_chunks=relevant_chunks,
                asset_class=asset_class,
                statement_type=statement_type
            )
            
            # Step 7: Validate and import
            validated_records = self._validate_records(extracted_data, asset_class)
            imported_count = self._import_to_database(validated_records, asset_class, user_id)
            
            return {
                'success': True,
                'count': imported_count,
                'records': validated_records,
                'statement_type': statement_type
            }
            
        except Exception as e:
            logger.error(f"Error importing PDF: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'count': 0
            }
    
    def _get_asset_schema(self, asset_class: str) -> Dict[str, Any]:
        """
        Get the database schema for a specific asset class
        This defines what fields we need to extract
        """
        schemas = {
            'equities': {
                'required': ['symbol', 'quantity', 'average_price'],
                'optional': ['company_name', 'isin', 'purchase_date', 'exchange'],
                'types': {
                    'symbol': 'string',
                    'quantity': 'integer',
                    'average_price': 'float',
                    'purchase_date': 'date'
                }
            },
            'mutual_funds': {
                'required': ['scheme_name', 'units', 'nav'],
                'optional': ['fund_house', 'folio_number', 'isin', 'purchase_date'],
                'types': {
                    'scheme_name': 'string',
                    'units': 'float',
                    'nav': 'float',
                    'purchase_date': 'date'
                }
            },
            'fixed_deposits': {
                'required': ['bank_name', 'principal_amount', 'interest_rate', 'start_date', 'maturity_date'],
                'optional': ['fd_number', 'interest_frequency', 'maturity_amount'],
                'types': {
                    'principal_amount': 'float',
                    'interest_rate': 'float',
                    'start_date': 'date',
                    'maturity_date': 'date'
                }
            },
            # Add more schemas for other asset classes
        }
        
        return schemas.get(asset_class, {})
    
    def _map_columns_with_llm(self, excel_columns: List[str], 
                             target_schema: Dict, asset_class: str) -> Dict[str, str]:
        """
        Use LLM to intelligently map Excel columns to database fields
        
        Example:
            Excel columns: ["Stock Name", "Qty", "Avg Cost"]
            Maps to: {"Stock Name": "symbol", "Qty": "quantity", "Avg Cost": "average_price"}
        """
        
        # Construct prompt for LLM
        prompt = f"""
You are a financial data mapping expert. Map the following Excel columns to the database schema for {asset_class}.

Excel Columns: {', '.join(excel_columns)}

Target Schema:
Required Fields: {', '.join(target_schema.get('required', []))}
Optional Fields: {', '.join(target_schema.get('optional', []))}

Return a JSON mapping where keys are Excel column names and values are database field names.
Only map columns that have a clear correspondence. Return empty string for unmapped columns.

Example:
{{"Stock Name": "symbol", "Qty": "quantity", "Avg Cost": "average_price"}}
"""
        
        # Call OpenAI API (using existing integration)
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial data mapping expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            mapping_json = response.choices[0].message.content
            mapping = json.loads(mapping_json)
            
            logger.info(f"Column mapping: {mapping}")
            return mapping
            
        except Exception as e:
            logger.error(f"Error in LLM column mapping: {str(e)}")
            # Fallback to simple string matching
            return self._fallback_column_mapping(excel_columns, target_schema)
    
    def _fallback_column_mapping(self, excel_columns: List[str], 
                                 target_schema: Dict) -> Dict[str, str]:
        """
        Simple string matching fallback if LLM fails
        """
        mapping = {}
        all_fields = target_schema.get('required', []) + target_schema.get('optional', [])
        
        for col in excel_columns:
            col_lower = col.lower().replace(' ', '_')
            for field in all_fields:
                if field.lower() in col_lower or col_lower in field.lower():
                    mapping[col] = field
                    break
        
        return mapping
    
    def _extract_records_from_excel(self, df: pd.DataFrame, 
                                   column_mapping: Dict[str, str],
                                   schema: Dict) -> List[Dict]:
        """
        Extract records from DataFrame using the column mapping
        """
        records = []
        
        for _, row in df.iterrows():
            record = {}
            for excel_col, db_field in column_mapping.items():
                if excel_col in df.columns and db_field:
                    value = row[excel_col]
                    # Convert to appropriate type based on schema
                    field_type = schema.get('types', {}).get(db_field, 'string')
                    record[db_field] = self._convert_value(value, field_type)
            
            if record:  # Only add non-empty records
                records.append(record)
        
        return records
    
    def _convert_value(self, value: Any, target_type: str) -> Any:
        """Convert value to target type"""
        try:
            if pd.isna(value):
                return None
            
            if target_type == 'integer':
                return int(float(value))
            elif target_type == 'float':
                return float(value)
            elif target_type == 'date':
                if isinstance(value, datetime):
                    return value.date()
                return pd.to_datetime(value).date()
            else:
                return str(value)
        except:
            return None
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _chunk_pdf_text(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split PDF text into semantic chunks"""
        # Simple chunking by character count with overlap
        chunks = []
        overlap = 200
        
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks using OpenAI"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            embeddings = []
            for chunk in chunks:
                response = openai.Embedding.create(
                    model="text-embedding-ada-002",
                    input=chunk
                )
                embeddings.append(response['data'][0]['embedding'])
            
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []
    
    def _generate_query_embeddings(self, asset_class: str, statement_type: str) -> List[float]:
        """Generate query embedding for finding relevant sections"""
        query = f"Extract {asset_class} holdings data from {statement_type} statement including quantities, prices, and dates"
        
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=query
            )
            return response['data'][0]['embedding']
        except:
            return []
    
    def _retrieve_relevant_chunks(self, chunk_embeddings: List[List[float]], 
                                 query_embedding: List[float],
                                 chunks: List[str], top_k: int = 5) -> List[str]:
        """Retrieve most relevant chunks using cosine similarity"""
        import numpy as np
        
        if not chunk_embeddings or not query_embedding:
            return chunks[:top_k]  # Fallback to first chunks
        
        # Calculate cosine similarity
        similarities = []
        for chunk_emb in chunk_embeddings:
            similarity = np.dot(chunk_emb, query_embedding) / (
                np.linalg.norm(chunk_emb) * np.linalg.norm(query_embedding)
            )
            similarities.append(similarity)
        
        # Get top K chunks
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        relevant_chunks = [chunks[i] for i in top_indices]
        
        return relevant_chunks
    
    def _extract_holdings_with_llm(self, relevant_chunks: List[str],
                                  asset_class: str, statement_type: str) -> List[Dict]:
        """
        Use LLM to extract structured holdings data from relevant text chunks
        """
        schema = self._get_asset_schema(asset_class)
        
        prompt = f"""
Extract {asset_class} holdings data from the following {statement_type} statement text.

Text:
{' '.join(relevant_chunks[:3])}  # Limit to first 3 chunks for token efficiency

Extract the following fields:
Required: {', '.join(schema.get('required', []))}
Optional: {', '.join(schema.get('optional', []))}

Return a JSON array of holdings objects. Each object should have the extracted fields.

Example format:
[
  {{"symbol": "RELIANCE", "quantity": 100, "average_price": 2500.50}},
  {{"symbol": "TCS", "quantity": 50, "average_price": 3200.00}}
]
"""
        
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial document parser expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            extracted_json = response.choices[0].message.content
            holdings = json.loads(extracted_json)
            
            return holdings
            
        except Exception as e:
            logger.error(f"Error extracting with LLM: {str(e)}")
            return []
    
    def _validate_records(self, records: List[Dict], asset_class: str) -> List[Dict]:
        """
        Validate extracted records against schema requirements
        """
        schema = self._get_asset_schema(asset_class)
        required_fields = schema.get('required', [])
        
        validated = []
        for record in records:
            # Check if all required fields are present
            if all(field in record and record[field] is not None for field in required_fields):
                validated.append(record)
            else:
                logger.warning(f"Skipping invalid record: {record}")
        
        return validated
    
    def _import_to_database(self, records: List[Dict], asset_class: str, user_id: int) -> int:
        """
        Import validated records to database
        Returns count of imported records
        """
        # TODO: Implement actual database insertion based on asset_class
        # This would use the appropriate model (ManualEquityHolding, ManualMutualFundHolding, etc.)
        
        logger.info(f"Would import {len(records)} records for {asset_class}")
        return len(records)


# Utility function for routes to use
def create_import_service():
    """Factory function to create DocumentImportService instance"""
    return DocumentImportService()
