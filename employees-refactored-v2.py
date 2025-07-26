from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Protocol, Type, TypeVar, Optional, Union
from enum import Enum
import os
import json
from pathlib import Path
from datetime import datetime

# CONFIGURATION

@dataclass
class AppConfig:
    """Application configuration to avoid magic numbers."""
    FIXED_VACATION_DAYS_PAYOUT: int = 5
    DEFAULT_MONTHLY_SALARY: float = 5000.0
    DEFAULT_HOURLY_RATE: float = 50.0
    DEFAULT_HOURS_WORKED: int = 10
    DEFAULT_VACATION_DAYS: int = 25
    PAYMENT_POLICIES_FILE: str = "payment_policies.json"
    # Bonificación constants
    SALARIED_BONUS_PERCENTAGE: float = 10.0  # 10% para asalariados
    HOURLY_BONUS_AMOUNT: float = 100.0       # $100 para empleados por hora
    HOURLY_BONUS_THRESHOLD: int = 160        # umbral de 160 horas

# Global configuration instance
config = AppConfig()

# PAYMENT POLICIES

@dataclass
class PaymentPolicy:
    """Dynamic payment policy configuration."""
    employee_type: str
    base_rate: float
    overtime_multiplier: float = 1.5
    bonus_percentage: float = 0.0
    max_hours_per_week: int = 40
    holiday_pay_multiplier: float = 1.0
    weekend_pay_multiplier: float = 1.0
    night_shift_bonus: float = 0.0
    performance_bonus_threshold: float = 0.0
    performance_bonus_percentage: float = 0.0

class PaymentPolicyManager:
    """Manages dynamic payment policies loaded from external sources."""
    
    def __init__(self, policies_file: str = config.PAYMENT_POLICIES_FILE):
        self.policies_file = policies_file
        self._policies: Dict[str, PaymentPolicy] = {}
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load payment policies from JSON file."""
        try:
            if Path(self.policies_file).exists():
                with open(self.policies_file, 'r', encoding='utf-8') as f:
                    policies_data = json.load(f)
                    for policy_data in policies_data.get('policies', []):
                        policy = PaymentPolicy(**policy_data)
                        self._policies[policy.employee_type] = policy
                print(f"Loaded {len(self._policies)} payment policies from {self.policies_file}")
            else:
                self._create_default_policies()
        except Exception as e:
            print(f"Error loading payment policies: {e}")
            self._create_default_policies()
    
    def _create_default_policies(self) -> None:
        """Create default payment policies if file doesn't exist."""
        default_policies = {
            'salaried': PaymentPolicy(
                employee_type='salaried',
                base_rate=config.DEFAULT_MONTHLY_SALARY,
                bonus_percentage=config.SALARIED_BONUS_PERCENTAGE,  # 10% bonificación
                performance_bonus_threshold=0.8,
                performance_bonus_percentage=5.0
            ),
            'hourly': PaymentPolicy(
                employee_type='hourly',
                base_rate=config.DEFAULT_HOURLY_RATE,
                overtime_multiplier=1.5,
                max_hours_per_week=40,
                weekend_pay_multiplier=1.25,
                night_shift_bonus=2.0
            ),
            'freelancer': PaymentPolicy(
                employee_type='freelancer',
                base_rate=0.0,  # Freelancers are paid per project
                bonus_percentage=15.0,
                performance_bonus_threshold=0.9,
                performance_bonus_percentage=10.0
            )
        }
        self._policies.update(default_policies)
        self._save_default_policies()
    
    def _save_default_policies(self) -> None:
        """Save default policies to JSON file."""
        try:
            policies_data = {
                'policies': [
                    {
                        'employee_type': policy.employee_type,
                        'base_rate': policy.base_rate,
                        'overtime_multiplier': policy.overtime_multiplier,
                        'bonus_percentage': policy.bonus_percentage,
                        'max_hours_per_week': policy.max_hours_per_week,
                        'holiday_pay_multiplier': policy.holiday_pay_multiplier,
                        'weekend_pay_multiplier': policy.weekend_pay_multiplier,
                        'night_shift_bonus': policy.night_shift_bonus,
                        'performance_bonus_threshold': policy.performance_bonus_threshold,
                        'performance_bonus_percentage': policy.performance_bonus_percentage
                    }
                    for policy in self._policies.values()
                ]
            }
            with open(self.policies_file, 'w', encoding='utf-8') as f:
                json.dump(policies_data, f, indent=2, ensure_ascii=False)
            print(f"Created default payment policies file: {self.policies_file}")
        except Exception as e:
            print(f"Error saving default policies: {e}")
    
    def get_policy(self, employee_type: str) -> PaymentPolicy:
        """Get payment policy for employee type."""
        policy = self._policies.get(employee_type)
        if not policy:
            raise ValueError(f"No payment policy found for employee type: {employee_type}")
        return policy
    
    def reload_policies(self) -> None:
        """Reload policies from file."""
        self._load_policies()
    
    def update_policy(self, employee_type: str, **kwargs) -> None:
        """Update a payment policy."""
        if employee_type not in self._policies:
            raise ValueError(f"No policy exists for employee type: {employee_type}")
        
        current_policy = self._policies[employee_type]
        for key, value in kwargs.items():
            if hasattr(current_policy, key):
                setattr(current_policy, key, value)
        
        self._save_policies()
    
    def _save_policies(self) -> None:
        """Save current policies to JSON file."""
        try:
            policies_data = {
                'policies': [
                    {
                        'employee_type': policy.employee_type,
                        'base_rate': policy.base_rate,
                        'overtime_multiplier': policy.overtime_multiplier,
                        'bonus_percentage': policy.bonus_percentage,
                        'max_hours_per_week': policy.max_hours_per_week,
                        'holiday_pay_multiplier': policy.holiday_pay_multiplier,
                        'weekend_pay_multiplier': policy.weekend_pay_multiplier,
                        'night_shift_bonus': policy.night_shift_bonus,
                        'performance_bonus_threshold': policy.performance_bonus_threshold,
                        'performance_bonus_percentage': policy.performance_bonus_percentage
                    }
                    for policy in self._policies.values()
                ]
            }
            with open(self.policies_file, 'w', encoding='utf-8') as f:
                json.dump(policies_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving policies: {e}")

# ENUMS AND CONSTANTS

class EmployeeRole(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"

class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"
    FREELANCER = "freelancer"

# INTERFACES

class PayrollCalculator(Protocol):
    def calculate_pay(self, employee: 'Employee') -> float: ...

class VacationManager(Protocol):
    def take_vacation(self, employee: 'Employee', payout: bool, days: int) -> None: ...

class EmployeeRepository(Protocol):
    def add_employee(self, employee: 'Employee') -> None: ...
    def get_all_employees(self) -> List['Employee']: ...
    def find_by_role(self, role: EmployeeRole) -> List['Employee']: ...

class UIRenderer(Protocol):
    def clear_screen(self) -> None: ...
    def display_menu(self, options: List[str]) -> None: ...
    def get_input(self, prompt: str) -> str: ...
    def display_message(self, message: str) -> None: ...

# DOMAIN MODELS

@dataclass
class Employee:
    name: str
    role: EmployeeRole
    vacation_days: int = config.DEFAULT_VACATION_DAYS
    performance_rating: float = 1.0  # 0.0 to 1.0
    night_shift_hours: int = 0
    weekend_hours: int = 0
    holiday_hours: int = 0

    def reduce_vacation_days(self, days: int) -> None:
        if self.vacation_days < days:
            raise ValueError(f"Insufficient vacation days. Available: {self.vacation_days}")
        self.vacation_days -= days

@dataclass
class SalariedEmployee(Employee):
    monthly_salary: float = config.DEFAULT_MONTHLY_SALARY

@dataclass
class HourlyEmployee(Employee):
    hourly_rate: float = config.DEFAULT_HOURLY_RATE
    hours_worked: int = config.DEFAULT_HOURS_WORKED

@dataclass
class FreelancerEmployee(Employee):
    projects: Dict[str, float] = field(default_factory=dict)

    def add_project(self, name: str, amount: float) -> None:
        self.projects[name] = amount

# STRATEGY IMPLEMENTATIONS

class SalariedPayrollCalculator:
    def __init__(self, policy_manager: PaymentPolicyManager):
        self.policy_manager = policy_manager
    
    def calculate_pay(self, employee: SalariedEmployee) -> float:
        policy = self.policy_manager.get_policy('salaried')
        
        # Base salary
        base_pay = employee.monthly_salary
        
        # BONIFICACIÓN POR DESEMPEÑO: 10% adicional (excepto pasantes)
        performance_bonus = 0.0
        if employee.role != EmployeeRole.INTERN:  # Los pasantes no reciben bonificación
            performance_bonus = base_pay * (config.SALARIED_BONUS_PERCENTAGE / 100)
        
        # Performance bonus adicional
        extra_performance_bonus = 0.0
        if employee.performance_rating >= policy.performance_bonus_threshold:
            extra_performance_bonus = base_pay * (policy.performance_bonus_percentage / 100)
        
        # Regular bonus from policy
        regular_bonus = base_pay * (policy.bonus_percentage / 100)
        
        total_pay = base_pay + performance_bonus + extra_performance_bonus + regular_bonus
        return total_pay

class HourlyPayrollCalculator:
    def __init__(self, policy_manager: PaymentPolicyManager):
        self.policy_manager = policy_manager
    
    def calculate_pay(self, employee: HourlyEmployee) -> float:
        policy = self.policy_manager.get_policy('hourly')
        
        # Regular hours (up to max_hours_per_week)
        regular_hours = min(employee.hours_worked, policy.max_hours_per_week)
        overtime_hours = max(0, employee.hours_worked - policy.max_hours_per_week)
        
        # Base pay for regular hours
        base_pay = regular_hours * employee.hourly_rate
        
        # Overtime pay
        overtime_pay = overtime_hours * employee.hourly_rate * policy.overtime_multiplier
        
        # BONIFICACIÓN POR DESEMPEÑO: $100 si > 160 horas (excepto pasantes)
        performance_bonus = 0.0
        if employee.role != EmployeeRole.INTERN and employee.hours_worked > config.HOURLY_BONUS_THRESHOLD:
            performance_bonus = config.HOURLY_BONUS_AMOUNT
        
        # Weekend pay
        weekend_pay = employee.weekend_hours * employee.hourly_rate * policy.weekend_pay_multiplier
        
        # Holiday pay
        holiday_pay = employee.holiday_hours * employee.hourly_rate * policy.holiday_pay_multiplier
        
        # Night shift bonus
        night_shift_pay = employee.night_shift_hours * policy.night_shift_bonus
        
        total_pay = base_pay + overtime_pay + performance_bonus + weekend_pay + holiday_pay + night_shift_pay
        return total_pay

class FreelancerPayrollCalculator:
    def __init__(self, policy_manager: PaymentPolicyManager):
        self.policy_manager = policy_manager
    
    def calculate_pay(self, employee: FreelancerEmployee) -> float:
        policy = self.policy_manager.get_policy('freelancer')
        
        # Base pay from projects
        base_pay = sum(employee.projects.values())
        
        # Performance bonus
        performance_bonus = 0.0
        if employee.performance_rating >= policy.performance_bonus_threshold:
            performance_bonus = base_pay * (policy.performance_bonus_percentage / 100)
        
        # Regular bonus
        regular_bonus = base_pay * (policy.bonus_percentage / 100)
        
        total_pay = base_pay + performance_bonus + regular_bonus
        return total_pay

# VACATION POLICIES BY ROLE

@dataclass
class VacationPolicy:
    """Specific vacation policies for different employee roles."""
    role: EmployeeRole
    base_vacation_days: int
    max_vacation_days: int
    payout_allowed: bool
    payout_days_limit: int
    carry_over_limit: int
    seniority_bonus_days: int = 0  # Additional days per year of service

class VacationPolicyManager:
    """Manages role-specific vacation policies."""
    
    def __init__(self):
        self._policies = {
            EmployeeRole.INTERN: VacationPolicy(
                role=EmployeeRole.INTERN,
                base_vacation_days=0,  # Interns cannot take vacations
                max_vacation_days=0,   # Interns cannot take vacations
                payout_allowed=False,
                payout_days_limit=0,
                carry_over_limit=0
            ),
            EmployeeRole.MANAGER: VacationPolicy(
                role=EmployeeRole.MANAGER,
                base_vacation_days=25,
                max_vacation_days=35,
                payout_allowed=True,
                payout_days_limit=10,  # Managers can get up to 10 days payout
                carry_over_limit=15,
                seniority_bonus_days=2
            ),
            EmployeeRole.VICE_PRESIDENT: VacationPolicy(
                role=EmployeeRole.VICE_PRESIDENT,
                base_vacation_days=30,
                max_vacation_days=5,   # Vice presidents limited to 5 days per request
                payout_allowed=True,
                payout_days_limit=5,   # Vice presidents limited to 5 days payout
                carry_over_limit=20,
                seniority_bonus_days=3
            )
        }
    
    def get_policy(self, role: EmployeeRole) -> VacationPolicy:
        """Get vacation policy for a specific role."""
        return self._policies.get(role, self._policies[EmployeeRole.INTERN])
    
    def can_take_vacation(self, employee: Employee, days: int) -> bool:
        """Check if employee can take vacation days."""
        policy = self.get_policy(employee.role)
        return employee.vacation_days >= days and days <= policy.max_vacation_days
    
    def can_payout_vacation(self, employee: Employee, days: int) -> bool:
        """Check if employee can get vacation payout."""
        policy = self.get_policy(employee.role)
        return (policy.payout_allowed and 
                employee.vacation_days >= days and 
                days <= policy.payout_days_limit)

# TRANSACTION HISTORY

@dataclass
class Transaction:
    """Base transaction record."""
    timestamp: datetime
    employee_name: str
    employee_role: EmployeeRole
    transaction_type: str
    amount: float = 0.0
    description: str = ""

@dataclass
class VacationTransaction(Transaction):
    """Vacation-related transaction."""
    days_taken: int = 0
    payout: bool = False
    remaining_days: int = 0

@dataclass
class PaymentTransaction(Transaction):
    """Payment-related transaction."""
    base_pay: float = 0.0
    bonuses: float = 0.0
    overtime: float = 0.0
    special_hours: float = 0.0
    performance_bonus: float = 0.0

class TransactionLogger:
    """Logs all transactions (vacations and payments)."""
    
    def __init__(self, log_file: str = "transaction_history.json"):
        self.log_file = log_file
        self._transactions: List[Dict] = []
        self._load_transactions()
    
    def _load_transactions(self) -> None:
        """Load existing transactions from file."""
        try:
            if Path(self.log_file).exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self._transactions = json.load(f)
        except Exception as e:
            print(f"Error loading transaction history: {e}")
            self._transactions = []
    
    def _save_transactions(self) -> None:
        """Save transactions to file."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self._transactions, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            print(f"Error saving transaction history: {e}")
    
    def log_vacation(self, employee: Employee, days: int, payout: bool, 
                    remaining_days: int, description: str = "") -> None:
        """Log a vacation transaction."""
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "employee_name": employee.name,
            "employee_role": employee.role.value,
            "transaction_type": "vacation",
            "days_taken": days,
            "payout": payout,
            "remaining_days": remaining_days,
            "description": description or f"{'Payout' if payout else 'Vacation'} of {days} days"
        }
        self._transactions.append(transaction)
        self._save_transactions()
    
    def log_payment(self, employee: Employee, total_amount: float, 
                   base_pay: float, bonuses: float, overtime: float = 0.0,
                   special_hours: float = 0.0, performance_bonus: float = 0.0) -> None:
        """Log a payment transaction."""
        transaction = {
            "timestamp": datetime.now().isoformat(),
            "employee_name": employee.name,
            "employee_role": employee.role.value,
            "transaction_type": "payment",
            "amount": total_amount,
            "base_pay": base_pay,
            "bonuses": bonuses,
            "overtime": overtime,
            "special_hours": special_hours,
            "performance_bonus": performance_bonus,
            "description": f"Payment: ${total_amount:.2f}"
        }
        self._transactions.append(transaction)
        self._save_transactions()
    
    def get_employee_history(self, employee_name: str) -> List[Dict]:
        """Get transaction history for a specific employee."""
        return [t for t in self._transactions if t["employee_name"] == employee_name]
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent transactions."""
        return sorted(self._transactions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_transactions_by_type(self, transaction_type: str) -> List[Dict]:
        """Get transactions by type (vacation or payment)."""
        return [t for t in self._transactions if t["transaction_type"] == transaction_type]
    
    def export_transaction_report(self, filename: str = None) -> None:
        """Export transaction history to a readable format."""
        if not filename:
            filename = f"transaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("TRANSACTION HISTORY REPORT\n")
                f.write("=" * 50 + "\n\n")
                
                for transaction in sorted(self._transactions, key=lambda x: x["timestamp"]):
                    f.write(f"Date: {transaction['timestamp']}\n")
                    f.write(f"Employee: {transaction['employee_name']} ({transaction['employee_role']})\n")
                    f.write(f"Type: {transaction['transaction_type'].upper()}\n")
                    
                    if transaction['transaction_type'] == 'vacation':
                        f.write(f"Days: {transaction['days_taken']} ({'Payout' if transaction['payout'] else 'Time Off'})\n")
                        f.write(f"Remaining: {transaction['remaining_days']} days\n")
                    else:  # payment
                        f.write(f"Total: ${transaction['amount']:.2f}\n")
                        f.write(f"  Base: ${transaction['base_pay']:.2f}\n")
                        f.write(f"  Bonuses: ${transaction['bonuses']:.2f}\n")
                        if transaction.get('overtime', 0) > 0:
                            f.write(f"  Overtime: ${transaction['overtime']:.2f}\n")
                        if transaction.get('special_hours', 0) > 0:
                            f.write(f"  Special Hours: ${transaction['special_hours']:.2f}\n")
                        if transaction.get('performance_bonus', 0) > 0:
                            f.write(f"  Performance Bonus: ${transaction['performance_bonus']:.2f}\n")
                    
                    f.write(f"Description: {transaction['description']}\n")
                    f.write("-" * 30 + "\n\n")
            
            print(f"Transaction report exported to: {filename}")
        except Exception as e:
            print(f"Error exporting transaction report: {e}")

# ENHANCED VACATION MANAGER WITH ROLE-SPECIFIC POLICIES

class EnhancedVacationManager:
    """Enhanced vacation manager with role-specific policies and transaction logging."""
    
    def __init__(self, vacation_policy_manager: VacationPolicyManager, transaction_logger: TransactionLogger):
        self.vacation_policy_manager = vacation_policy_manager
        self.transaction_logger = transaction_logger
    
    def take_vacation(self, employee: Employee, payout: bool, days: int) -> None:
        """Take vacation with role-specific policies and logging."""
        if isinstance(employee, FreelancerEmployee):
            print("Freelancers do not have vacation benefits.")
            return
        
        # Special handling for interns
        if employee.role == EmployeeRole.INTERN:
            raise ValueError("Interns cannot request vacations or receive vacation payouts.")
        
        policy = self.vacation_policy_manager.get_policy(employee.role)
        
        # Validate vacation request
        if payout:
            if not self.vacation_policy_manager.can_payout_vacation(employee, days):
                raise ValueError(f"Payout not allowed for {employee.role.value} or insufficient days")
        else:
            if not self.vacation_policy_manager.can_take_vacation(employee, days):
                raise ValueError(f"Cannot take {days} days. Available: {employee.vacation_days}, Max: {policy.max_vacation_days}")
        
        # Apply vacation
        original_days = employee.vacation_days
        employee.reduce_vacation_days(days)
        
        # Log transaction
        description = f"{'Payout' if payout else 'Vacation'} for {employee.role.value}"
        self.transaction_logger.log_vacation(
            employee=employee,
            days=days,
            payout=payout,
            remaining_days=employee.vacation_days,
            description=description
        )
        
        # Display result
        action = "Paying out" if payout else "Taking"
        print(f"{action} {days} vacation days for {employee.name} ({employee.role.value})")
        print(f"Remaining vacation days: {employee.vacation_days}")

# CALCULATOR REGISTRY

class PayrollCalculatorRegistry:
    """Registry pattern to map employee types to their calculators."""
    
    def __init__(self, policy_manager: PaymentPolicyManager):
        self.policy_manager = policy_manager
        self._calculators: Dict[Type[Employee], PayrollCalculator] = {}
    
    def register(self, employee_type: Type[Employee], calculator: PayrollCalculator) -> None:
        """Register a calculator for an employee type."""
        self._calculators[employee_type] = calculator
    
    def get_calculator(self, employee_type: Type[Employee]) -> PayrollCalculator:
        """Get the calculator for an employee type."""
        calculator = self._calculators.get(employee_type)
        if not calculator:
            raise ValueError(f"No calculator registered for {employee_type.__name__}")
        return calculator
    
    def calculate_pay(self, employee: Employee) -> float:
        """Calculate pay for an employee using the appropriate calculator."""
        calculator = self.get_calculator(type(employee))
        return calculator.calculate_pay(employee)

# UI

class ConsoleUIRenderer:
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    def display_menu(self, options: List[str]) -> None:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
    def get_input(self, prompt: str) -> str:
        return input(prompt)
    def display_message(self, message: str) -> None:
        print(message)

# REPOSITORY

class InMemoryEmployeeRepository:
    def __init__(self):
        self._employees: List[Employee] = []
    def add_employee(self, employee: Employee) -> None:
        self._employees.append(employee)
    def get_all_employees(self) -> List[Employee]:
        return self._employees.copy()
    def find_by_role(self, role: EmployeeRole) -> List[Employee]:
        return [e for e in self._employees if e.role == role]

# FACTORIES

class AbstractEmployeeFactory(ABC):
    @abstractmethod
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee: ...

class SalariedEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return SalariedEmployee(
            name=name, 
            role=role, 
            monthly_salary=kwargs.get("monthly_salary", config.DEFAULT_MONTHLY_SALARY),
            performance_rating=kwargs.get("performance_rating", 1.0)
        )

class HourlyEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return HourlyEmployee(
            name=name, 
            role=role,
            hourly_rate=kwargs.get("hourly_rate", config.DEFAULT_HOURLY_RATE),
            hours_worked=kwargs.get("hours_worked", config.DEFAULT_HOURS_WORKED),
            performance_rating=kwargs.get("performance_rating", 1.0),
            night_shift_hours=kwargs.get("night_shift_hours", 0),
            weekend_hours=kwargs.get("weekend_hours", 0),
            holiday_hours=kwargs.get("holiday_hours", 0)
        )

class FreelancerEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return FreelancerEmployee(
            name=name, 
            role=role, 
            projects=kwargs.get("projects", {}),
            performance_rating=kwargs.get("performance_rating", 1.0)
        )

class EmployeeFactoryProvider:
    @staticmethod
    def get_factory(employee_type: EmployeeType) -> AbstractEmployeeFactory:
        factories = {
            EmployeeType.SALARIED: SalariedEmployeeFactory(),
            EmployeeType.HOURLY: HourlyEmployeeFactory(),
            EmployeeType.FREELANCER: FreelancerEmployeeFactory()
        }
        return factories[employee_type]

# INPUT VALIDATORS

class EmployeeInputValidator:
    """Validates employee input data."""
    
    @staticmethod
    def validate_name(name: str) -> str:
        if not name.strip():
            raise ValueError("Name cannot be empty")
        return name.strip()
    
    @staticmethod
    def validate_role(role_str: str) -> EmployeeRole:
        try:
            return EmployeeRole(role_str.lower())
        except ValueError:
            raise ValueError(f"Invalid role. Must be one of: {[r.value for r in EmployeeRole]}")
    
    @staticmethod
    def validate_employee_type(type_str: str) -> EmployeeType:
        try:
            return EmployeeType(type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid employee type. Must be one of: {[t.value for t in EmployeeType]}")
    
    @staticmethod
    def validate_salary(salary_str: str) -> float:
        try:
            salary = float(salary_str)
            if salary <= 0:
                raise ValueError("Salary must be positive")
            return salary
        except ValueError:
            raise ValueError("Invalid salary amount")
    
    @staticmethod
    def validate_hourly_rate(rate_str: str) -> float:
        try:
            rate = float(rate_str)
            if rate <= 0:
                raise ValueError("Hourly rate must be positive")
            return rate
        except ValueError:
            raise ValueError("Invalid hourly rate")
    
    @staticmethod
    def validate_hours_worked(hours_str: str) -> int:
        try:
            hours = int(hours_str)
            if hours <= 0:
                raise ValueError("Hours worked must be positive")
            return hours
        except ValueError:
            raise ValueError("Invalid hours worked")
    
    @staticmethod
    def validate_performance_rating(rating_str: str) -> float:
        try:
            rating = float(rating_str)
            if rating < 0.0 or rating > 1.0:
                raise ValueError("Performance rating must be between 0.0 and 1.0")
            return rating
        except ValueError:
            raise ValueError("Invalid performance rating")

# COMANDO PARA VACACIONES

class GrantVacationCommand:
    def __init__(self, vacation_manager: VacationManager, ui: UIRenderer,
                 employee: Employee, payout: bool, days: int):
        self._vacation_manager = vacation_manager
        self._ui = ui
        self._employee = employee
        self._payout = payout
        self._days = days

    def execute(self) -> None:
        try:
            self._vacation_manager.take_vacation(self._employee, self._payout, self._days)
        except Exception as e:
            self._ui.display_message(f"Error: {e}")

# SERVICIO DE PAGO

class EnhancedPayrollService:
    """Enhanced payroll service with detailed transaction logging."""
    
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer, 
                 policy_manager: PaymentPolicyManager, transaction_logger: TransactionLogger):
        self._repository = repository
        self._ui = ui
        self._policy_manager = policy_manager
        self._transaction_logger = transaction_logger
        self._calculator_registry = PayrollCalculatorRegistry(policy_manager)
        self._setup_calculators()
    
    def _setup_calculators(self) -> None:
        """Setup the calculator registry with all employee types."""
        self._calculator_registry.register(SalariedEmployee, SalariedPayrollCalculator(self._policy_manager))
        self._calculator_registry.register(HourlyEmployee, HourlyPayrollCalculator(self._policy_manager))
        self._calculator_registry.register(FreelancerEmployee, FreelancerPayrollCalculator(self._policy_manager))

    def pay_all_employees(self) -> None:
        """Pagar todos los empleados con bonificaciones automáticas y logging detallado."""
        employees = self._repository.get_all_employees()
        
        if not employees:
            self._ui.display_message("No employees to pay.")
            return
        
        self._ui.display_message("\n--- PAYROLL REPORT WITH PERFORMANCE BONUSES ---")
        total_payroll = 0.0
        
        for emp in employees:
            try:
                # Calculate detailed pay breakdown
                pay_breakdown = self._calculate_detailed_pay(emp)
                total_amount = pay_breakdown['total']
                total_payroll += total_amount
                
                # Log payment transaction
                self._transaction_logger.log_payment(
                    employee=emp,
                    total_amount=total_amount,
                    base_pay=pay_breakdown['base_pay'],
                    bonuses=pay_breakdown['bonuses'],
                    overtime=pay_breakdown.get('overtime', 0.0),
                    special_hours=pay_breakdown.get('special_hours', 0.0),
                    performance_bonus=pay_breakdown.get('performance_bonus', 0.0)
                )
                
                # Mostrar detalle de bonificación
                bonus_info = self._get_bonus_info(emp)
                self._ui.display_message(f"Paying {emp.name}: ${total_amount:.2f} {bonus_info}")
                
            except Exception as e:
                self._ui.display_message(f"Error paying {emp.name}: {e}")
        
        self._ui.display_message(f"\nTotal Payroll: ${total_payroll:.2f}")
    
    def _calculate_detailed_pay(self, emp: Employee) -> Dict[str, float]:
        """Calculate detailed pay breakdown for logging."""
        if isinstance(emp, SalariedEmployee):
            policy = self._policy_manager.get_policy('salaried')
            base_pay = emp.monthly_salary
            
            # Performance bonus (10% for non-interns)
            performance_bonus = 0.0
            if emp.role != EmployeeRole.INTERN:
                performance_bonus = base_pay * (config.SALARIED_BONUS_PERCENTAGE / 100)
            
            # Extra performance bonus from policy
            extra_performance_bonus = 0.0
            if emp.performance_rating >= policy.performance_bonus_threshold:
                extra_performance_bonus = base_pay * (policy.performance_bonus_percentage / 100)
            
            # Regular bonus from policy
            regular_bonus = base_pay * (policy.bonus_percentage / 100)
            
            total_bonuses = performance_bonus + extra_performance_bonus + regular_bonus
            total_pay = base_pay + total_bonuses
            
            return {
                'total': total_pay,
                'base_pay': base_pay,
                'bonuses': total_bonuses,
                'performance_bonus': performance_bonus + extra_performance_bonus
            }
            
        elif isinstance(emp, HourlyEmployee):
            policy = self._policy_manager.get_policy('hourly')
            
            # Regular hours
            regular_hours = min(emp.hours_worked, policy.max_hours_per_week)
            overtime_hours = max(0, emp.hours_worked - policy.max_hours_per_week)
            
            base_pay = regular_hours * emp.hourly_rate
            overtime_pay = overtime_hours * emp.hourly_rate * policy.overtime_multiplier
            
            # Performance bonus ($100 if > 160 hours, except interns)
            performance_bonus = 0.0
            if emp.role != EmployeeRole.INTERN and emp.hours_worked > config.HOURLY_BONUS_THRESHOLD:
                performance_bonus = config.HOURLY_BONUS_AMOUNT
            
            # Special hours
            weekend_pay = emp.weekend_hours * emp.hourly_rate * policy.weekend_pay_multiplier
            holiday_pay = emp.holiday_hours * emp.hourly_rate * policy.holiday_pay_multiplier
            night_shift_pay = emp.night_shift_hours * policy.night_shift_bonus
            special_hours_total = weekend_pay + holiday_pay + night_shift_pay
            
            total_pay = base_pay + overtime_pay + performance_bonus + special_hours_total
            
            return {
                'total': total_pay,
                'base_pay': base_pay,
                'bonuses': performance_bonus,
                'overtime': overtime_pay,
                'special_hours': special_hours_total,
                'performance_bonus': performance_bonus
            }
            
        elif isinstance(emp, FreelancerEmployee):
            policy = self._policy_manager.get_policy('freelancer')
            base_pay = sum(emp.projects.values())
            
            # Performance bonus
            performance_bonus = 0.0
            if emp.performance_rating >= policy.performance_bonus_threshold:
                performance_bonus = base_pay * (policy.performance_bonus_percentage / 100)
            
            # Regular bonus
            regular_bonus = base_pay * (policy.bonus_percentage / 100)
            total_bonuses = performance_bonus + regular_bonus
            
            total_pay = base_pay + total_bonuses
            
            return {
                'total': total_pay,
                'base_pay': base_pay,
                'bonuses': total_bonuses,
                'performance_bonus': performance_bonus
            }
        
        return {'total': 0.0, 'base_pay': 0.0, 'bonuses': 0.0}
    
    def _get_bonus_info(self, emp: Employee) -> str:
        """Obtiene información sobre la bonificación aplicada."""
        if emp.role == EmployeeRole.INTERN:
            return "(No bonus - Intern)"
        
        if isinstance(emp, SalariedEmployee):
            return f"(+{config.SALARIED_BONUS_PERCENTAGE}% performance bonus)"
        elif isinstance(emp, HourlyEmployee):
            if emp.hours_worked > config.HOURLY_BONUS_THRESHOLD:
                return f"(+${config.HOURLY_BONUS_AMOUNT} performance bonus - {emp.hours_worked}hrs > {config.HOURLY_BONUS_THRESHOLD})"
            else:
                return f"(No performance bonus - {emp.hours_worked}hrs ≤ {config.HOURLY_BONUS_THRESHOLD})"
        
        return ""
    
    def reload_policies(self) -> None:
        """Reload payment policies from file."""
        self._policy_manager.reload_policies()
        self._ui.display_message("Payment policies reloaded successfully!")

# APP PRINCIPAL

class EmployeeManagementApp:
    def __init__(self, repo: EmployeeRepository, ui: UIRenderer, vacation_manager: EnhancedVacationManager):
        self.repo = repo
        self.ui = ui
        self.vacation_manager = vacation_manager
        self.policy_manager = PaymentPolicyManager()
        self.transaction_logger = TransactionLogger()
        self.payroll_service = EnhancedPayrollService(repo, ui, self.policy_manager, self.transaction_logger)
        self.validator = EmployeeInputValidator()

    def run(self):
        while True:
            self.ui.clear_screen()
            self.ui.display_menu([
                "Create employee",
                "Grant vacation",
                "View employees",
                "Pay employees",  # Con bonificaciones automáticas
                "Manage payment policies",
                "View transaction history",
                "Export transaction report",
                "Exit"
            ])
            choice = self.ui.get_input("Choice: ")
            if choice == "1":
                self._create_employee()
            elif choice == "2":
                self._grant_vacation()
            elif choice == "3":
                self._view_employees()
            elif choice == "4":
                self.payroll_service.pay_all_employees()  # Incluye bonificaciones automáticas
            elif choice == "5":
                self._manage_payment_policies()
            elif choice == "6":
                self._view_transaction_history()
            elif choice == "7":
                self._export_transaction_report()
            elif choice == "8":
                break
            else:
                self.ui.display_message("Invalid choice.")
            self.ui.get_input("Press Enter to continue...")

    def _create_employee(self):
        """Create a new employee with input validation."""
        try:
            name = self._get_employee_name()
            role = self._get_employee_role()
            emp_type = self._get_employee_type()
            kwargs = self._get_employee_specific_data(emp_type)
            
            factory = EmployeeFactoryProvider.get_factory(emp_type)
            employee = factory.create_employee(name, role, **kwargs)
            self.repo.add_employee(employee)
            self.ui.display_message("Employee created successfully!")
        except Exception as e:
            self.ui.display_message(f"Error creating employee: {e}")

    def _get_employee_name(self) -> str:
        """Get and validate employee name."""
        name = self.ui.get_input("Name: ")
        return self.validator.validate_name(name)

    def _get_employee_role(self) -> EmployeeRole:
        """Get and validate employee role."""
        role_input = self.ui.get_input("Role (intern/manager/vice_president): ")
        return self.validator.validate_role(role_input)

    def _get_employee_type(self) -> EmployeeType:
        """Get and validate employee type."""
        type_input = self.ui.get_input("Type (salaried/hourly/freelancer): ")
        return self.validator.validate_employee_type(type_input)

    def _get_employee_specific_data(self, emp_type: EmployeeType) -> Dict:
        """Get employee type-specific data with validation."""
        kwargs = {}

        if emp_type == EmployeeType.SALARIED:
            salary_input = self.ui.get_input("Monthly salary: ")
            kwargs["monthly_salary"] = self.validator.validate_salary(salary_input)
        elif emp_type == EmployeeType.HOURLY:
            rate_input = self.ui.get_input("Hourly rate: ")
            kwargs["hourly_rate"] = self.validator.validate_hourly_rate(rate_input)
            hours_input = self.ui.get_input("Hours worked: ")
            kwargs["hours_worked"] = self.validator.validate_hours_worked(hours_input)
            
            # Additional hourly employee data
            night_hours = self.ui.get_input("Night shift hours (0 if none): ")
            kwargs["night_shift_hours"] = int(night_hours) if night_hours.isdigit() else 0
            
            weekend_hours = self.ui.get_input("Weekend hours (0 if none): ")
            kwargs["weekend_hours"] = int(weekend_hours) if weekend_hours.isdigit() else 0
            
            holiday_hours = self.ui.get_input("Holiday hours (0 if none): ")
            kwargs["holiday_hours"] = int(holiday_hours) if holiday_hours.isdigit() else 0
            
        elif emp_type == EmployeeType.FREELANCER:
            kwargs["projects"] = self._get_freelancer_projects()

        # Performance rating for all employee types
        rating_input = self.ui.get_input("Performance rating (0.0-1.0, default 1.0): ")
        if rating_input.strip():
            kwargs["performance_rating"] = self.validator.validate_performance_rating(rating_input)
        else:
            kwargs["performance_rating"] = 1.0

        return kwargs

    def _get_freelancer_projects(self) -> Dict[str, float]:
        """Get freelancer project data."""
        projects = {}
        self.ui.display_message("Enter project details (leave project name empty to finish):")
        
        while True:
            pname = self.ui.get_input("Project name: ").strip()
            if not pname:
                break
            try:
                amount = float(self.ui.get_input(f"Amount for '{pname}': "))
                if amount <= 0:
                    self.ui.display_message("Project amount must be positive")
                    continue
                projects[pname] = amount
            except ValueError:
                self.ui.display_message("Invalid project amount")
                continue
        
        return projects

    def _manage_payment_policies(self):
        """Manage payment policies."""
        while True:
            self.ui.clear_screen()
            self.ui.display_menu([
                "View current policies",
                "Reload policies from file",
                "Update policy",
                "Back to main menu"
            ])
            choice = self.ui.get_input("Choice: ")
            
            if choice == "1":
                self._view_payment_policies()
            elif choice == "2":
                self.payroll_service.reload_policies()
            elif choice == "3":
                self._update_payment_policy()
            elif choice == "4":
                break
            else:
                self.ui.display_message("Invalid choice.")
            
            if choice != "4":
                self.ui.get_input("Press Enter to continue...")

    def _view_payment_policies(self):
        """Display current payment policies."""
        self.ui.display_message("Current Payment Policies:")
        self.ui.display_message("=" * 50)
        
        for emp_type in ['salaried', 'hourly', 'freelancer']:
            try:
                policy = self.policy_manager.get_policy(emp_type)
                self.ui.display_message(f"\n{emp_type.upper()} EMPLOYEE POLICY:")
                self.ui.display_message(f"  Base Rate: ${policy.base_rate}")
                self.ui.display_message(f"  Overtime Multiplier: {policy.overtime_multiplier}x")
                self.ui.display_message(f"  Bonus Percentage: {policy.bonus_percentage}%")
                self.ui.display_message(f"  Max Hours per Week: {policy.max_hours_per_week}")
                self.ui.display_message(f"  Performance Bonus Threshold: {policy.performance_bonus_threshold}")
                self.ui.display_message(f"  Performance Bonus Percentage: {policy.performance_bonus_percentage}%")
            except Exception as e:
                self.ui.display_message(f"Error loading {emp_type} policy: {e}")

    def _update_payment_policy(self):
        """Update a payment policy."""
        self.ui.display_message("Available employee types: salaried, hourly, freelancer")
        emp_type = self.ui.get_input("Enter employee type to update: ").lower()
        
        if emp_type not in ['salaried', 'hourly', 'freelancer']:
            self.ui.display_message("Invalid employee type.")
            return
        
        try:
            current_policy = self.policy_manager.get_policy(emp_type)
            self.ui.display_message(f"Current {emp_type} policy loaded.")
            
            # Get new values
            new_base_rate = self.ui.get_input(f"New base rate (current: {current_policy.base_rate}): ")
            if new_base_rate.strip():
                self.policy_manager.update_policy(emp_type, base_rate=float(new_base_rate))
            
            new_overtime = self.ui.get_input(f"New overtime multiplier (current: {current_policy.overtime_multiplier}): ")
            if new_overtime.strip():
                self.policy_manager.update_policy(emp_type, overtime_multiplier=float(new_overtime))
            
            new_bonus = self.ui.get_input(f"New bonus percentage (current: {current_policy.bonus_percentage}): ")
            if new_bonus.strip():
                self.policy_manager.update_policy(emp_type, bonus_percentage=float(new_bonus))
            
            self.ui.display_message(f"{emp_type} policy updated successfully!")
            
        except Exception as e:
            self.ui.display_message(f"Error updating policy: {e}")

    def _view_transaction_history(self):
        """View transaction history with filtering options."""
        while True:
            self.ui.clear_screen()
            self.ui.display_menu([
                "View all recent transactions",
                "View employee-specific history",
                "View vacation transactions only",
                "View payment transactions only",
                "Back to main menu"
            ])
            choice = self.ui.get_input("Choice: ")
            
            if choice == "1":
                self._show_recent_transactions()
            elif choice == "2":
                self._show_employee_history()
            elif choice == "3":
                self._show_vacation_transactions()
            elif choice == "4":
                self._show_payment_transactions()
            elif choice == "5":
                break
            else:
                self.ui.display_message("Invalid choice.")
            
            if choice != "5":
                self.ui.get_input("Press Enter to continue...")

    def _show_recent_transactions(self):
        """Show recent transactions."""
        transactions = self.transaction_logger.get_recent_transactions(10)
        if not transactions:
            self.ui.display_message("No transactions found.")
            return
        
        self.ui.display_message("Recent Transactions:")
        self.ui.display_message("=" * 50)
        
        for i, transaction in enumerate(transactions, 1):
            self.ui.display_message(f"\n{i}. {transaction['timestamp'][:19]} - {transaction['employee_name']}")
            self.ui.display_message(f"   Type: {transaction['transaction_type'].upper()}")
            if transaction['transaction_type'] == 'vacation':
                self.ui.display_message(f"   Days: {transaction['days_taken']} ({'Payout' if transaction['payout'] else 'Time Off'})")
            else:
                self.ui.display_message(f"   Amount: ${transaction['amount']:.2f}")

    def _show_employee_history(self):
        """Show transaction history for a specific employee."""
        employees = self.repo.get_all_employees()
        if not employees:
            self.ui.display_message("No employees found.")
            return
        
        self.ui.display_message("Select employee to view history:")
        for i, emp in enumerate(employees, 1):
            self.ui.display_message(f"{i}. {emp.name}")
        
        try:
            choice = int(self.ui.get_input("Enter employee number: ")) - 1
            if 0 <= choice < len(employees):
                employee = employees[choice]
                transactions = self.transaction_logger.get_employee_history(employee.name)
                
                if not transactions:
                    self.ui.display_message(f"No transactions found for {employee.name}")
                    return
                
                self.ui.display_message(f"\nTransaction History for {employee.name}:")
                self.ui.display_message("=" * 50)
                
                for transaction in transactions:
                    self.ui.display_message(f"\n{transaction['timestamp'][:19]} - {transaction['transaction_type'].upper()}")
                    if transaction['transaction_type'] == 'vacation':
                        self.ui.display_message(f"  Days: {transaction['days_taken']} ({'Payout' if transaction['payout'] else 'Time Off'})")
                        self.ui.display_message(f"  Remaining: {transaction['remaining_days']} days")
                    else:
                        self.ui.display_message(f"  Amount: ${transaction['amount']:.2f}")
                        self.ui.display_message(f"  Base: ${transaction['base_pay']:.2f}, Bonuses: ${transaction['bonuses']:.2f}")
            else:
                self.ui.display_message("Invalid employee number.")
        except ValueError:
            self.ui.display_message("Invalid input.")

    def _show_vacation_transactions(self):
        """Show only vacation transactions."""
        transactions = self.transaction_logger.get_transactions_by_type('vacation')
        if not transactions:
            self.ui.display_message("No vacation transactions found.")
            return
        
        self.ui.display_message("Vacation Transactions:")
        self.ui.display_message("=" * 50)
        
        for transaction in transactions:
            self.ui.display_message(f"\n{transaction['timestamp'][:19]} - {transaction['employee_name']}")
            self.ui.display_message(f"  Days: {transaction['days_taken']} ({'Payout' if transaction['payout'] else 'Time Off'})")
            self.ui.display_message(f"  Remaining: {transaction['remaining_days']} days")

    def _show_payment_transactions(self):
        """Show only payment transactions."""
        transactions = self.transaction_logger.get_transactions_by_type('payment')
        if not transactions:
            self.ui.display_message("No payment transactions found.")
            return
        
        self.ui.display_message("Payment Transactions:")
        self.ui.display_message("=" * 50)
        
        total_payments = 0.0
        for transaction in transactions:
            self.ui.display_message(f"\n{transaction['timestamp'][:19]} - {transaction['employee_name']}")
            self.ui.display_message(f"  Total: ${transaction['amount']:.2f}")
            self.ui.display_message(f"  Base: ${transaction['base_pay']:.2f}, Bonuses: ${transaction['bonuses']:.2f}")
            if transaction.get('overtime', 0) > 0:
                self.ui.display_message(f"  Overtime: ${transaction['overtime']:.2f}")
            if transaction.get('performance_bonus', 0) > 0:
                self.ui.display_message(f"  Performance Bonus: ${transaction['performance_bonus']:.2f}")
            total_payments += transaction['amount']
        
        self.ui.display_message(f"\nTotal Payments: ${total_payments:.2f}")

    def _export_transaction_report(self):
        """Export transaction history to a file."""
        try:
            filename = self.ui.get_input("Enter filename (or press Enter for default): ").strip()
            if not filename:
                filename = None
            
            self.transaction_logger.export_transaction_report(filename)
            self.ui.display_message("Transaction report exported successfully!")
        except Exception as e:
            self.ui.display_message(f"Error exporting report: {e}")

    def _grant_vacation(self):
        employees = self.repo.get_all_employees()
        if not employees:
            self.ui.display_message("No employees available.")
            return

        # Show employees with vacation policy info
        self.ui.display_message("Employees and their vacation policies:")
        for i, emp in enumerate(employees):
            if isinstance(emp, FreelancerEmployee):
                self.ui.display_message(f"{i}. {emp.name} - Freelancer (No vacation benefits)")
            elif emp.role == EmployeeRole.INTERN:
                self.ui.display_message(f"{i}. {emp.name} ({emp.role.value}) - Cannot take vacations or receive payouts")
            else:
                policy = self.vacation_manager.vacation_policy_manager.get_policy(emp.role)
                self.ui.display_message(f"{i}. {emp.name} ({emp.role.value}) - {emp.vacation_days} days left")
                self.ui.display_message(f"   Policy: {policy.base_vacation_days} base days, max {policy.max_vacation_days}, payout: {'Yes' if policy.payout_allowed else 'No'}")

        try:
            idx = int(self.ui.get_input("Select employee index: "))
            if idx < 0 or idx >= len(employees):
                raise ValueError("Invalid index")

            emp = employees[idx]
            
            if isinstance(emp, FreelancerEmployee):
                self.ui.display_message("Freelancers do not have vacation benefits.")
                return
            
            # Check if employee is an intern
            if emp.role == EmployeeRole.INTERN:
                self.ui.display_message("Interns cannot request vacations or receive vacation payouts.")
                return
            
            # Get vacation type and days
            payout = self.ui.get_input("Payout instead of time off? (y/n): ").lower() == "y"
            
            if payout:
                policy = self.vacation_manager.vacation_policy_manager.get_policy(emp.role)
                if not policy.payout_allowed:
                    self.ui.display_message(f"Payout not allowed for {emp.role.value} employees.")
                    return
                days = int(self.ui.get_input(f"How many days to payout? (max {policy.payout_days_limit}): "))
            else:
                days = int(self.ui.get_input("How many vacation days?: "))
            
            # Use enhanced vacation manager directly
            self.vacation_manager.take_vacation(emp, payout, days)
            
        except Exception as e:
            self.ui.display_message(f"Error: {e}")

    def _view_employees(self):
        employees = self.repo.get_all_employees()
        if not employees:
            self.ui.display_message("No employees found.")
            return
            
        for emp in employees:
            self.ui.display_message(f"{emp.name} - {emp.role.value} - {emp.vacation_days} days - Performance: {emp.performance_rating}")
            if isinstance(emp, FreelancerEmployee):
                for pname, amt in emp.projects.items():
                    self.ui.display_message(f"  Project: {pname}, Amount: ${amt}")
            elif isinstance(emp, HourlyEmployee):
                self.ui.display_message(f"  Hours: {emp.hours_worked}, Rate: ${emp.hourly_rate}")
                if emp.night_shift_hours > 0 or emp.weekend_hours > 0 or emp.holiday_hours > 0:
                    self.ui.display_message(f"  Special hours - Night: {emp.night_shift_hours}, Weekend: {emp.weekend_hours}, Holiday: {emp.holiday_hours}")
            elif isinstance(emp, SalariedEmployee):
                self.ui.display_message(f"  Monthly Salary: ${emp.monthly_salary}")

# MAIN

def main():
    repo = InMemoryEmployeeRepository()
    ui = ConsoleUIRenderer()
    vacation_manager = EnhancedVacationManager(VacationPolicyManager(), TransactionLogger())
    app = EmployeeManagementApp(repo, ui, vacation_manager)
    app.run()

if __name__ == "__main__":
    main()