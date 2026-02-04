# syntax=docker/dockerfile:1
#*******************************************************************************
# Copyright (c) 2025 CreamCollar Edtech pvt ltd
#
# This file is part of the CreamCollar AUTOSAR MCAL Generator project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#*******************************************************************************


FROM python:3.11-slim

# Install system dependencies for tkinter
RUN apt-get update && apt-get install -y python3-tk

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . . 

CMD ["python", "main.py"]
