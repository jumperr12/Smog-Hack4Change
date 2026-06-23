from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/routes")
async def websocket_trasy(websocket: WebSocket) -> None:
    """
    Szkielet WebSocket do streamowania postępu optymalizacji trasy w czasie rzeczywistym.

    TODO: Zaimplementować:
    - streaming etapów RouteOptimizer (pobieranie tras → próbkowanie → ranking)
    - push aktualizacji jakości powietrza gdy stacje odświeżą dane
    - alerty o wejściu w strefę wysokiego smogu podczas nawigacji
    """
    await websocket.accept()
    try:
        while True:
            dane = await websocket.receive_text()
            # Na razie echo — zastąpić strumieniowaniem RouteOptimizer
            await websocket.send_text(f"echo: {dane}")
    except WebSocketDisconnect:
        pass
