-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 30, 2022 at 04:53 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.0.19

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `qrcode_attendance`
--

-- --------------------------------------------------------

--
-- Table structure for table `attendance_sched`
--

CREATE TABLE `attendance_sched` (
  `sched_id` varchar(255) NOT NULL,
  `date` varchar(255) NOT NULL,
  `time_in_start` varchar(255) NOT NULL,
  `time_in_end` varchar(255) NOT NULL,
  `time_out_start` varchar(255) NOT NULL,
  `time_out_end` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `attendance_sched`
--

INSERT INTO `attendance_sched` (`sched_id`, `date`, `time_in_start`, `time_in_end`, `time_out_start`, `time_out_end`) VALUES
('72a0d27a-9fbe-4f4f-b1d3-069cfbc89685', '2022-08-29', '6:00:00', '7:30:00', '16:00:00', '18:30:00');

-- --------------------------------------------------------

--
-- Table structure for table `records`
--

CREATE TABLE `records` (
  `record_id` varchar(255) NOT NULL,
  `sched_id` varchar(255) NOT NULL,
  `user_id` varchar(255) NOT NULL,
  `time_in` varchar(255) NOT NULL,
  `time_out` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `records`
--

INSERT INTO `records` (`record_id`, `sched_id`, `user_id`, `time_in`, `time_out`) VALUES
('3694a979-51d1-4ea8-97e5-d5fceb55c704', '72a0d27a-9fbe-4f4f-b1d3-069cfbc89685', '417e4a6e-5e8a-47fe-97ec-4ce822122943', '22:45:56', '');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` varchar(255) NOT NULL,
  `fname` varchar(255) NOT NULL,
  `lname` varchar(255) NOT NULL,
  `qrcode` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `fname`, `lname`, `qrcode`, `address`, `email`) VALUES
('417e4a6e-5e8a-47fe-97ec-4ce822122943', 'Richard', 'Divino', '417e4a6e-5e8a-47fe-97ec-4ce822122943.png', 'P-6 Barobo, Bahi, Surigao del Sur', 'richarddivino128@gmail.com');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `attendance_sched`
--
ALTER TABLE `attendance_sched`
  ADD PRIMARY KEY (`sched_id`);

--
-- Indexes for table `records`
--
ALTER TABLE `records`
  ADD PRIMARY KEY (`record_id`),
  ADD KEY `sched_id` (`sched_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
