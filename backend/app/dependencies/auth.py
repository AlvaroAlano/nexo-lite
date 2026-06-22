from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt as pyjwt
from uuid import UUID
from app.config import settings

security = HTTPBearer(auto_error=False)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UUID:
    """
    Decodifica o token JWT fornecido pelo Supabase Auth.
    Retorna o user_id (UUID) extraído do payload.
    Em modo desenvolvimento (sem SUPABASE_JWT_SECRET), decodifica o token sem validar a assinatura.
    Se nenhum token for enviado, retorna settings.DEMO_USER_ID para compatibilidade.
    """
    if not credentials:
        return settings.DEMO_USER_ID

    token = credentials.credentials
    try:
        if settings.SUPABASE_JWT_SECRET:
            payload = pyjwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
        else:
            payload = pyjwt.decode(token, options={"verify_signature": False})
        
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: campo 'sub' ausente."
            )
        return UUID(user_id_str)
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado."
        )
    except (pyjwt.InvalidTokenError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou malformado: {str(e)}"
        )
