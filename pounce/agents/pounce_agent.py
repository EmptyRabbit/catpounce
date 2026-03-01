import os
from uuid import uuid4

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from pounce.agent.base import BaseAgent
from pounce.agent.node.distribute import DistributeNode
from pounce.agents.state import PounceState


class PounceAgent(BaseAgent):
    def __init__(self, model, report_path: str = None):
        super().__init__(model)
        self.report_path = report_path

    async def get_graph(self):
        distribute_node = DistributeNode(self.model)

        builder = StateGraph(PounceState, input_schema=PounceState)
        builder.add_node('distribute', distribute_node.distribute)
        builder.add_node('browser_agent', self.call_browser_agent)

        builder.add_edge(START, 'distribute')
        builder.add_conditional_edges(
            source='distribute',
            path=self.is_task_finish,
            path_map={False: 'distribute', True: END}
        )

        memory = MemorySaver()
        graph = builder.compile(name="Pounce Agent", checkpointer=memory)
        return graph

    async def run(self, user_msg: str, max_step: int = 100) -> PounceState:
        task_id = uuid4().hex
        task_report_path = os.path.join(self.report_path, task_id)

        input_state = PounceState(
            user_message=user_msg,
            report_path=task_report_path,
            task_id=task_id
        )
        resp = await self.ainvoke(input=input_state, recursion_limit=max_step)
        return resp
