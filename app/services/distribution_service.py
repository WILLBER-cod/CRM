import random
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Operator, Source, Lead, Contact, OperatorSourceWeight

class DistributionService:
    
    @staticmethod
    def find_or_create_lead(db: Session, external_id: str = None, email: str = None, phone: str = None) -> Lead:
        """Найти или создать лида по уникальным данным"""
        lead = None
        
        # Поиск по external_id
        if external_id:
            lead = db.query(Lead).filter(Lead.external_id == external_id).first()
        
        # Поиск по email
        if not lead and email:
            lead = db.query(Lead).filter(Lead.email == email).first()
        
        # Поиск по телефону
        if not lead and phone:
            lead = db.query(Lead).filter(Lead.phone == phone).first()
        
        # Создание нового лида
        if not lead:
            lead = Lead(
                external_id=external_id,
                email=email,
                phone=phone
            )
            db.add(lead)
            db.commit()
            db.refresh(lead)
        
        return lead
    
    @staticmethod
    def get_available_operators(db: Session, source_id: int) -> List[Operator]:
        """Получить доступных операторов для источника"""
        # Находим операторов с весами для данного источника
        operator_weights = db.query(OperatorSourceWeight).filter(
            OperatorSourceWeight.source_id == source_id
        ).all()
        
        available_operators = []
        
        for ow in operator_weights:
            operator = db.query(Operator).filter(
                Operator.id == ow.operator_id,
                Operator.is_active == True,
                Operator.current_load < Operator.max_load
            ).first()
            
            if operator:
                available_operators.append({
                    'operator': operator,
                    'weight': ow.weight
                })
        
        return available_operators
    
    @staticmethod
    def select_operator(available_operators: List) -> Optional[Operator]:
        """Выбрать оператора по весам"""
        if not available_operators:
            return None
        
        # Взвешенный случайный выбор
        total_weight = sum(op['weight'] for op in available_operators)
        random_value = random.uniform(0, total_weight)
        
        current_weight = 0
        for op_data in available_operators:
            current_weight += op_data['weight']
            if random_value <= current_weight:
                return op_data['operator']
        
        # На случай ошибки округления возвращаем первого
        return available_operators[0]['operator']
    
    @staticmethod
    def distribute_contact(db: Session, contact_data: dict) -> Contact:
        """Распределить обращение между операторами"""
        # Находим или создаем лида
        lead = DistributionService.find_or_create_lead(
            db=db,
            external_id=contact_data.get('lead_external_id'),
            email=contact_data.get('lead_email'),
            phone=contact_data.get('lead_phone')
        )
        
        # Получаем доступных операторов
        available_operators = DistributionService.get_available_operators(
            db=db, 
            source_id=contact_data['source_id']
        )
        
        # Выбираем оператора
        selected_operator = DistributionService.select_operator(available_operators)
        
        # Создаем обращение
        contact = Contact(
            lead_id=lead.id,
            source_id=contact_data['source_id'],
            operator_id=selected_operator.id if selected_operator else None,
            message=contact_data.get('message')
        )
        
        db.add(contact)
        
        # Обновляем нагрузку оператора
        if selected_operator:
            selected_operator.current_load += 1
        
        db.commit()
        db.refresh(contact)
        
        return contact
