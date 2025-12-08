import { useContext } from "react";
import { GlobalContext } from "../context/GlobalContext";
import { FaSpinner } from "react-icons/fa";

const Loading = () => {
    const { loading } = useContext(GlobalContext);

    return (
        <div id="loading" className={loading ? "loading active" : "loading"}>
            <span className="icon">
                <FaSpinner className="fa-spin" />
            </span>
        </div>
    );
};

export { Loading };