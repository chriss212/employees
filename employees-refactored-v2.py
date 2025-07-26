from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Protocol, Type, TypeVar, Optional
from enum import Enum
import os
import json
from pathlib import Path

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

class StandardVacationManager:
    def take_vacation(self, employee: Employee, payout: bool, days: int) -> None:
        if isinstance(employee, FreelancerEmployee):
            print("Freelancers do not have vacation benefits.")
            return
        if payout:
            employee.reduce_vacation_days(config.FIXED_VACATION_DAYS_PAYOUT)
        else:
            employee.reduce_vacation_days(days)

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

class PayrollService:
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer, policy_manager: PaymentPolicyManager):
        self._repository = repository
        self._ui = ui
        self._policy_manager = policy_manager
        self._calculator_registry = PayrollCalculatorRegistry(policy_manager)
        self._setup_calculators()
    
    def _setup_calculators(self) -> None:
        """Setup the calculator registry with all employee types."""
        self._calculator_registry.register(SalariedEmployee, SalariedPayrollCalculator(self._policy_manager))
        self._calculator_registry.register(HourlyEmployee, HourlyPayrollCalculator(self._policy_manager))
        self._calculator_registry.register(FreelancerEmployee, FreelancerPayrollCalculator(self._policy_manager))

    def pay_all_employees(self) -> None:
        """Pagar todos los empleados con bonificaciones automáticas."""
        employees = self._repository.get_all_employees()
        
        if not employees:
            self._ui.display_message("No employees to pay.")
            return
        
        self._ui.display_message("\n--- PAYROLL REPORT WITH PERFORMANCE BONUSES ---")
        total_payroll = 0.0
        
        for emp in employees:
            try:
                amount = self._calculator_registry.calculate_pay(emp)
                total_payroll += amount
                
                # Mostrar detalle de bonificación
                bonus_info = self._get_bonus_info(emp)
                self._ui.display_message(f"Paying {emp.name}: ${amount:.2f} {bonus_info}")
                
            except Exception as e:
                self._ui.display_message(f"Error paying {emp.name}: {e}")
        
        self._ui.display_message(f"\nTotal Payroll: ${total_payroll:.2f}")
    
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
    def __init__(self, repo: EmployeeRepository, ui: UIRenderer, vacation_manager: VacationManager):
        self.repo = repo
        self.ui = ui
        self.vacation_manager = vacation_manager
        self.policy_manager = PaymentPolicyManager()
        self.payroll_service = PayrollService(repo, ui, self.policy_manager)
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

    def _grant_vacation(self):
        employees = self.repo.get_all_employees()
        if not employees:
            self.ui.display_message("No employees available.")
            return

        for i, emp in enumerate(employees):
            self.ui.display_message(f"{i}. {emp.name} ({emp.vacation_days} days left)")

        try:
            idx = int(self.ui.get_input("Select employee index: "))
            if idx < 0 or idx >= len(employees):
                raise ValueError("Invalid index")

            emp = employees[idx]
            payout = self.ui.get_input("Payout instead of time off? (y/n): ").lower() == "y"
            days = config.FIXED_VACATION_DAYS_PAYOUT if payout else int(self.ui.get_input("How many vacation days?: "))
            cmd = GrantVacationCommand(self.vacation_manager, self.ui, emp, payout, days)
            cmd.execute()
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
    vacation_manager = StandardVacationManager()
    app = EmployeeManagementApp(repo, ui, vacation_manager)
    app.run()

if __name__ == "__main__":
    main()