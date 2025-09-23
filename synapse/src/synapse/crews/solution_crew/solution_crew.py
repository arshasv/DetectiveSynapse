from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from synapse.utils.llm import llm
from pydantic import BaseModel

class KeyFlaw(BaseModel):
    """Represents a key flaw in the crime plan that makes it solvable"""
    clueID: str
    description: str

class SolvablePath(BaseModel):
    """Represents the solvable path to the crime resolution"""
    keyFlaws: List[KeyFlaw]

class Solution(BaseModel):
    """Main solution model containing the solvable path"""
    solvablePath: SolvablePath


@CrewBase
class SolutionCrew:
    """Solution Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def Solution_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["Solution_agent"],
            llm=llm
        )

    @task
    def Generate_solution(self) -> Task:
        return Task(
            config=self.tasks_config["Generate_solution_task"],
            output_json=Solution
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Solution Crew"""

        return Crew(
            agents=self.agents,  
            tasks=self.tasks,  
            process=Process.sequential,
            verbose=True,
        )
