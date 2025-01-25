/**
 * @file LRSCFController_python.cpp
 *
 * @date Jan 22, 2025
 * @author Anton Rikus
 * @copyright \n
 *  This file is part of the program Serenity.\n\n
 *  Serenity is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Lesser General Public License as
 *  published by the Free Software Foundation, either version 3 of
 *  the License, or (at your option) any later version.\n\n
 *  Serenity is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.\n\n
 *  You should have received a copy of the GNU Lesser General
 *  Public License along with Serenity.
 *  If not, see <http://www.gnu.org/licenses/>.\n
 */

/* Include Serenity Internal Headers */
#include "postHF/LRSCF/LRSCFController.h"
/* Include Std and External Headers */
#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>

namespace py = pybind11;
using namespace Serenity;

void export_LRSCFController(py::module& spy) {
  py::class_ < LRSCFController, std::shared_ptr<LRSCFController<RESTRICTED>>(spy, "LRSCFController_R");
  .def(py::init<std::shared_ptr<SystemController>&, LRSCFTaskSettings&>())
}