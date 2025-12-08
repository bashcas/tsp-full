import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { GlobalContext } from "../context/GlobalContext";

const ProtectedRoute = ({ children }) => {
    const { local, routes } = useContext(GlobalContext);

    if (!local?.token) {
        return <Navigate to={routes.AccountRoute} replace />;
    }

    return children;
};

export { ProtectedRoute };
