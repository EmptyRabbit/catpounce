import os
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from pounce.agent.base import BaseAgent
from pounce.agent.node.planning import PlanningNode
from pounce.agent.node.action import ActionExecutorNode
from pounce.agent.node.action_check import ActionCheckNode
from pounce.agent.node.distribute import DistributeNode
from pounce.agent.prompt import get_prompt
from pounce.agent.schema.agent_schema import PounceContext, PounceState, PounceInputState


class PounceAgent(BaseAgent):
    def __init__(self, model, browser, report_path: str = None):
        super().__init__(model)
        self.browser = browser
        self.report_path = report_path

    @property
    def system_prompt(self):
        result = get_prompt('system_prompt.md')
        return result

    def is_planning_continue(self, state: PounceState):
        result = state.is_planning_continue()
        return result

    def is_task_finish(self, state: PounceState):
        result = state.is_task_finish()
        return result

    async def get_subtask_graph(self):
        planning_node = PlanningNode(self.model, self.system_prompt)
        action_node = ActionExecutorNode(self.model)
        action_check_node = ActionCheckNode(self.model)

        builder = StateGraph(PounceState, context_schema=PounceContext)
        builder.add_node("planning", planning_node.get_next_action)
        builder.add_node("action", action_node.route)
        builder.add_node("action_check", action_check_node.check)

        builder.add_edge(START, "planning")
        builder.add_conditional_edges(
            source="planning",
            path=self.is_planning_continue,
            path_map={True: 'action', False: END}
        )
        builder.add_conditional_edges(
            source="action",
            path=self.is_planning_continue,
            path_map={True: 'action_check', False: END}
        )
        builder.add_edge('action_check', 'planning')

        subgraph = builder.compile(name="Pounce SubTask Graph")
        return subgraph

    async def get_graph(self):
        distribute_node = DistributeNode(self.model)
        subgraph = await self.get_subtask_graph()

        builder = StateGraph(PounceState, input_schema=PounceInputState, context_schema=PounceContext)
        builder.add_node('distribute', distribute_node.distribute)
        builder.add_node('run_task', subgraph)

        builder.add_edge(START, 'distribute')
        builder.add_edge('distribute', 'run_task')
        builder.add_conditional_edges(
            source='run_task',
            path=self.is_task_finish,
            path_map={False: 'distribute', True: END}
        )

        memory = MemorySaver()
        graph = builder.compile(name="Pounce Agent", checkpointer=memory)
        return graph

    async def run(self, user_msg: str, max_step: int = 100, max_history_item: int = 20) -> PounceState:
        task_id = uuid4().hex
        task_report_path = os.path.join(self.report_path, task_id)

        async with self.browser as browser_instance:
            input_state = PounceInputState(
                user_message=user_msg,
                report_path=task_report_path,
                max_history_item=max_history_item,
                task_id=task_id
            )
            resp = await self.ainvoke(
                input=input_state,
                context=PounceContext(browser=browser_instance),
                recursion_limit=max_step
            )
            return resp
