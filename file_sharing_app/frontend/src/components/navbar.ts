
import api from "../api";

export const fetchUserData = async () => {
  const res = await api.get("/user_data");
  const data = res.data;
  return {
    username:data.username||"",
    email:data.email||"",
    dob:data.dob||null,
    url:data.avatarurl||"",
  };
};

