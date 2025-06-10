function Profile() {
  return (
    <div className="container d-flex justify-content-center align-items-center vh-100">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 w-full max-w-sm p-6 text-center">
        <div className="flex justify-center mb-4">
          <img
            src="https://via.placeholder.com/120"
            alt="Profile"
            className="w-28 h-28 rounded-full object-cover border-4 border-white shadow"
          />
        </div>

        <h2 className="text-2xl font-bold text-gray-800 mb-1">Username</h2>

        <div className="flex flex-col space-y-2">
          <button
            className="w-full bg-blue-700 font-medium py-2 rounded-md shadow hover:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-400 transition"
            aria-label="Edit Name"
          >
            Edit Name
          </button>
          <button
            className="w-full bg-gray-900 font-medium py-2 rounded-md shadow hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-500 transition"
            aria-label="Edit Password"
          >
            Edit Password
          </button>
        </div>
      </div>
    </div>
  );
}

export default Profile;
