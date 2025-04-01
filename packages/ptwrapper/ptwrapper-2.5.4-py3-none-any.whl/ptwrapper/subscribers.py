import os

from osve.osve_subscriber import OsvePtrAbstract

#from phs.modelling.swi import swi_violation
import spiceypy as spice


class OsvePtrLogger(OsvePtrAbstract):
    """
    A logger class that captures and logs PTR (Pointing Timeline Request) block data, extending
    from the OsvePtrAbstract class.

    Attributes
    ----------
    blocks_data : list
        A list that stores block data for each logged block in the PTR.
    """
    blocks_data = []

    def __init__(self, meta_kernel):
        """
        Initializes the logger by invoking the parent class's constructor and setting
        the logger name to 'theOsvePtrLogger'.
        """
        super().__init__("theOsvePtrLogger")
        self.mk = meta_kernel
        spice.furnsh(self.mk)
        mk = self.mk.split(os.sep)[-1]
        print(f'[INFO]    {"<PTWR>":<27} SPICE Meta-Kernel {mk} loaded for constraint checks')


#    def onSimulationStart(self, data):
#        #print(f'[INFO]    {"<PTWR>":<27} SWI constraint checks active')
#        spice.furnsh(self.mk)
#        mk = self.mk.split(os.sep)[-1]
#        print(f'[INFO]    {"<PTWR>":<27} SPICE Meta-Kernel {mk} loaded for constraint checks')


    def onPtrBlockEnd(self, blockData):
        """
        Appends the block data to the logger's list when a block ends.

        Parameters
        ----------
        blockData : dict
            A dictionary containing the data for a completed PTR block.

        Returns
        -------
        int
            Always returns 0, indicating successful logging of the block.
        """
        self.blocks_data.append(blockData)
        return 0

    def log(self, verbose=False):
        """
        Processes and logs block data, focusing on blocks containing errors,
        and generates a log summary.
        """
        ptr_log = {}
        idx = 1
        for block_data in self.blocks_data:
            if self._has_errors(block_data):
                if block_data["block_type"] != "SLEW":
                    self._process_standard_block(block_data, ptr_log, idx, verbose)
                else:
                    self._process_slew_block(block_data, ptr_log, idx, verbose)
            idx += 1

        # Unload SPICE Kernels
        spice.kclear()

        return ptr_log

    def _has_errors(self, block_data):
        """
        Checks if the block contains any error logs.
        """
        return any(log["severity"] == "ERROR" for log in block_data.get("block_logs", []))

    def _process_standard_block(self, block_data, ptr_log, idx, verbose):
        """
        Processes a standard (non-SLEW) block and updates the log.
        """
        designer, designer_obs = self._get_designer_and_obs(block_data)
        if verbose:
            self._print_block_summary(idx, designer, designer_obs, block_data["block_start"], block_data["block_end"])

        # Carry-out the constraint checks for SWI.
        #self._swi_constraint_check(block_data)

        error_messages = self._extract_error_messages(block_data, verbose)

        if designer not in ptr_log:
            ptr_log[designer] = {}
        ptr_log[designer][f"Block ({idx})"] = {
            "observation": designer_obs,
            "start_time": str(block_data["block_start"]),
            "end_time": str(block_data["block_end"]),
            "error_messages": error_messages,
        }

    def _process_slew_block(self, block_data, ptr_log, idx, verbose):
        """
        Processes a SLEW block and updates the log.
        """
        prev_info = self._get_slew_context(idx - 2, default_designer="SOC")
        next_info = self._get_slew_context(idx, default_designer="SOC")

        if verbose:
            self._print_slew_summary(idx, prev_info, next_info)

        error_messages = self._extract_error_messages(block_data, verbose, slew_prev=prev_info, slew_next=next_info)

        if prev_info and isinstance(prev_info, dict) and "designer" in prev_info:
            self._update_slew_log(ptr_log, prev_info, next_info, idx, error_messages)
        else:
            print(f'[WARNING] {"<PTWR>":<27} The SLEW block {idx-1} cannot be logged.')


    def _get_designer_and_obs(self, block_data):
        """
        Extracts the designer and observation details from the block data.
        """
        if "observations" in block_data:
            designer = block_data["observations"]["designer"]
            observations = block_data["observations"]["observations"]
            for observation in observations:
                if observation["unit"] == designer:
                    return designer, observation["definition"]
        return "SOC", f'{block_data["block_type"]} {block_data["block_mode"]}'

    def _extract_error_messages(self, block_data, verbose, slew_prev=None, slew_next=None):
        """
        Extracts error messages from the block logs.
        """
        error_messages = []
        for log_data in block_data.get("block_logs", []):
            if log_data["severity"] != "DEBUG" and log_data["module"] == "AGM":

                # Calculate the % of the error within the PTR Block. Requires special treatment if it is a slew.
                time_exec = spice.utc2et(str(log_data['time']))
                if slew_next and slew_prev:
                    time_start = spice.utc2et(str(slew_prev['time']))
                    time_end = spice.utc2et(str(slew_next['time']))
                else:
                    time_start = spice.utc2et(str(block_data["block_start"]))
                    time_end = spice.utc2et(str(block_data["block_end"]))


                try:
                    exec_percentage =  (time_exec - time_start)/(time_end - time_start)*100
                    exec_percentage = f'{exec_percentage:.0f}%'
                except:
                    exec_percentage = '-'

                error_message = f"      {log_data['severity']} , {exec_percentage}, {log_data['time']} , {log_data['text']}"
                if verbose:
                    print(error_message)
                error_messages.append({
                    "severity": log_data["severity"],
                    "percentage": exec_percentage,
                    "time": log_data["time"],
                    "text": log_data["text"],
                })
        return error_messages

    def _get_slew_context(self, index, default_designer="SOC"):
        """
        Gets context (designer, observation, and time) for a SLEW block.
        """
        try:
            block = self.blocks_data[index]
            designer = block["observations"]["designer"]
            observations = block["observations"]["observations"]
            for observation in observations:
                if observation["unit"] == designer:
                    return {
                        "designer": designer,
                        "obs": observation["definition"],
                        "time": str(block["block_end"]) if index < len(self.blocks_data) - 1 else str(
                            block["block_start"]),
                    }
        except (IndexError, KeyError):
            return {
                "designer": default_designer,
                "obs": f'{self.blocks_data[index]["block_type"]} {self.blocks_data[index]["block_mode"]}',
                "time": str(self.blocks_data[index]["block_start"]),
            }

    def _update_slew_log(self, ptr_log, prev_info, next_info, idx, error_messages):
        """
        Updates the log for a SLEW block.
        """
        if prev_info["designer"] not in ptr_log:
            ptr_log[prev_info["designer"]] = {}
        ptr_log[prev_info["designer"]][f"Block ({idx - 1}) SLEW AFTER"] = {
            "observation": prev_info["obs"],
            "start_time": prev_info["time"],
            "end_time": next_info["time"],
            "error_messages": error_messages,
        }

        if next_info["designer"] not in ptr_log:
            ptr_log[next_info["designer"]] = {}
        ptr_log[next_info["designer"]][f"Block ({idx + 1}) SLEW BEFORE"] = {
            "observation": next_info["obs"],
            "start_time": prev_info["time"],
            "end_time": next_info["time"],
            "error_messages": error_messages,
        }

    def _print_block_summary(self, idx, designer, designer_obs, start_time, end_time):
        """
        Prints a summary of a standard block.
        """
        print(f"BLOCK {idx} | {designer} | {designer_obs} | {start_time} - {end_time}")

    def _print_slew_summary(self, idx, prev_info, next_info):
        """
        Prints a summary of a SLEW block.
        """
        print(
            f"BLOCK {idx} | {prev_info['designer']},{next_info['designer']} | SLEW | "
            f"{prev_info['time']} ({prev_info['obs']}) - {next_info['time']} ({next_info['obs']})"
        )

    #def _swi_constraint_check(self, block_data):
    #
    #    et = spice.utc2et(block_data.data["time"])
    #    #violation = swi_violation(et = et, target = 'JUPITER', verbose = False)