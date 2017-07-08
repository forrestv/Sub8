#include <sub8_vision_lib/stereo_base.hpp>

#include <boost/python.hpp>
#include <boost/python/class.hpp>
#include <boost/python/module_init.hpp>
#include <boost/python/def.hpp>
#include <boost/python/call_method.hpp>
#include <boost/ref.hpp>
#include <boost/utility.hpp>

using namespace boost::python;

// class StereoBaseCallback : public StereoBase
// {
// public:
// 	StereoBaseCallback(PyObject *p) : self(p) {}
//     std::vector<cv::Point> get_2d_feature_points(cv::Mat image) { return call_method<std::vector<cv::Point>>(self, "get_2d_feature_points", image); }

// 	// virtual std::vector<cv::Point> get_2d_feature_points(cv::Mat image) {}
// 	// std::vector<cv::Point> get_2d_feature_points(cv::Mat image) { return call_method<std::vector<cv::Point>>(self, "pure", image); }
//     PyObject* self;
// };

// BOOST_PYTHON_MODULE(stereo_base_wrapper)
// {    // Create the Python type object for our extension class and define __init__ function.
//     // class_<StereoBaseCallback>("stereo_base")
//     // class_<StereoBase, StereoBaseCallback >("stereo_base")
//     //     .def("refresh_rate_", &StereoBaseCallback::refresh_rate_)  // Add invite() as a regular function to the module.
//     // ;
//     class_<StereoBase, boost::noncopyable, boost::shared_ptr<StereoBaseCallback> >("StereoBase")
//          .def("refresh_rate_", &StereoBase::refresh_rate_);
// }

// struct baz {
//     virtual int pure(int) = 0;
//     int calls_pure(int x) { return pure(x) + 1000; }
// };

// struct baz_callback : baz {
//     baz_callback(PyObject *p) : self(p) {}
//     int pure(int x) { return call_method<int>(self, "pure", x); }
//     PyObject *self;
// };

// BOOST_PYTHON_MODULE_INIT(foobar2)
// {
//      class_<baz, boost::noncopyable, boost::shared_ptr<baz_callback> >("baz")
//          .def("calls_pure", &baz::calls_pure);
// }



using namespace boost::python;

class baz {
public:
    virtual int pure(int) = 0;
    int calls_pure(int x) { return pure(x) + 1000; }
	int test_var;
};

class baz_callback : public baz {
public:
    baz_callback(PyObject *p) : self(p) {}
    int pure(int x) { return call_method<int>(self, "pure", x); }
    PyObject *self;
};

BOOST_PYTHON_MODULE_INIT(stereo_base_wrapper)
{
     class_<baz, boost::noncopyable, boost::shared_ptr<baz_callback> >("baz")
         .def("calls_pure", &baz::calls_pure)
         .def_readwrite("test_var", &baz::test_var);
}