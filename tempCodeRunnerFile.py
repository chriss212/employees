from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Protocol
from enum import Enum
import os

# ENUMS AND CONSTANTS

class EmployeeRole(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"

class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"

FIXED_VACATION_DAYS_PAYOUT = 5

# INTERFACES AND PROTOCOLS

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
    vacation_days: int = 25

    def reduce_vacation_days(self, days: int) -> None:
        if self.vacation_days < days:
            raise ValueError(f"Insufficient vacation days. Available: {self.vacation_days}")
        self.vacation_days -= days

@dataclass
class SalariedEmployee(Employee):
    monthly_salary: float = 5000.0

@dataclass
class HourlyEmployee(Employee):
    hourly_rate: float = 50.0
    hours_worked: int = 10

# STRATEGY IMPLEMENTATIONS

class SalariedPayrollCalculator:
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, SalariedEmployee):
            raise ValueError("Employee must be salaried")
        return employee.monthly_salary

class HourlyPayrollCalculator:
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, HourlyEmployee):
            raise ValueError("Employee must be hourly")
        return employee.hourly_rate * employee.hours_worked

class StandardVacationManager:
    def take_vacation(self, employee: Employee, payout: bool, days: int) -> None:
        if payout:
            self._handle_payout(employee)
        else:
            self._handle_time_off(employee, days)

    def _handle_payout(self, employee: Employee) -> None:
        employee.reduce_vacation_days(FIXED_VACATION_DAYS_PAYOUT)
        print(f"Paying out vacation. Holidays left: {employee.vacation_days}")

    def _handle_time_off(self, employee: Employee, days: int) -> None:
        employee.reduce_vacation_days(days)
        print(f"Enjoy your {days} days off! Remaining vacation days: {employee.vacation_days}")

class ConsoleUIRenderer:
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self, options: List[str]) -> None:
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")

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
        return [emp for emp in self._employees if emp.role == role]

# FACTORIES

class AbstractEmployeeFactory(ABC):
    @abstractmethod
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee: ...
    @abstractmethod
    def get_payroll_calculator(self) -> PayrollCalculator: ...

class SalariedEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        salary = kwargs.get('monthly_salary', 5000.0)
        return SalariedEmployee(name=name, role=role, monthly_salary=salary)

    def get_payroll_calculator(self) -> PayrollCalculator:
        return SalariedPayrollCalculator()

class HourlyEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        rate = kwargs.get('hourly_rate', 50.0)
        hours = kwargs.get('hours_worked', 10)
        return HourlyEmployee(name=name, role=role, hourly_rate=rate, hours_worked=hours)

    def get_payroll_calculator(self) -> PayrollCalculator:
        return HourlyPayrollCalculator()

class EmployeeFactoryProvider:
    @staticmethod
    def get_factory(employee_type: EmployeeType) -> AbstractEmployeeFactory:
        factories = {
            EmployeeType.SALARIED: SalariedEmployeeFactory(),
            EmployeeType.HOURLY: HourlyEmployeeFactory()
        }
        return factories[employee_type]

# COMMANDS

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

# APP

class EmployeeManagementApp:
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer,
                 vacation_manager: VacationManager):
        self._repository = repository
        self._ui = ui
        self._vacation_manager = vacation_manager

    def run(self) -> None:
        while True:
            self._ui.clear_screen()
            self._ui.display_message("--- Employee Management Menu ---")
            self._ui.display_menu([
                "Create employee",
                "Grant vacation to an employee",
                "View employees",
                "Exit"
            ])
            choice = self._ui.get_input("Select an option: ")

            if choice == "1":
                self._handle_create_employee()
            elif choice == "2":
                self._handle_grant_vacation()
            elif choice == "3":
                self._handle_view_employees()
            elif choice == "4":
                self._ui.display_message("Goodbye!")
                break
            else:
                self._ui.display_message("Invalid option.")

            self._ui.get_input("Press Enter to continue...")

    def _handle_create_employee(self) -> None:
        name = self._ui.get_input("Employee name: ")
        role = EmployeeRole(self._ui.get_input("Role (intern/manager/vice_president): ").lower())
        emp_type = EmployeeType(self._ui.get_input("Type (salaried/hourly): ").lower())

        if emp_type == EmployeeType.SALARIED:
            salary = float(self._ui.get_input("Monthly salary: "))
            employee = SalariedEmployee(name=name, role=role, monthly_salary=salary)
        else:
            rate = float(self._ui.get_input("Hourly rate: "))
            hours = int(self._ui.get_input("Hours worked: "))
            employee = HourlyEmployee(name=name, role=role, hourly_rate=rate, hours_worked=hours)

        self._repository.add_employee(employee)
        self._ui.display_message("Employee created successfully.")

    def _handle_view_employees(self) -> None:
        employees = self._repository.get_all_employees()
        for emp in employees:
            self._ui.display_message(f"{emp.name} - {emp.role.value} - {emp.vacation_days} vacation days")

    def _handle_grant_vacation(self) -> None:
        employees = self._repository.get_all_employees()
        if not employees:
            self._ui.display_message("No employees available.")
            return

        for idx, emp in enumerate(employees):
            self._ui.display_message(f"{idx}. {emp.name} ({emp.vacation_days} days left)")

        idx = int(self._ui.get_input("Select employee index: "))
        payout = self._ui.get_input("Payout instead of days off? (y/n): ").lower() == "y"
        days = FIXED_VACATION_DAYS_PAYOUT if payout else int(self._ui.get_input("Days to take: "))
        command = GrantVacationCommand(self._vacation_manager, self._ui, employees[idx], payout, days)
        command.execute()

# MAIN

def main():
    repository = InMemoryEmployeeRepository()
    ui = ConsoleUIRenderer()
    vacation_manager = StandardVacationManager()
    app = EmployeeManagementApp(repository, ui, vacation_manager)
    app.run()

if __name__ == "__main__":
    main()