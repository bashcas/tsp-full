
import { FaSuitcase } from "react-icons/fa";
const HistoryEmpty = () => {
    return (
        <div className="empty">
            <div className="icon">
                <FaSuitcase />
            </div>
            <span>you don't have trips yet</span>
        </div>
    )
};

export { HistoryEmpty };